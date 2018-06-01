# -*- coding: utf-8 -*-

import getpass
import argparse
import logging 
from classes.dbConnection import dbConnection
from classes.helperFunctions import helperFunctions
#LBSN Structure Import from ProtoBuf
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import io
import sys
import shapely.geometry as geometry
from shapely.geometry.polygon import Polygon
#Old Structure in Python:
#from classes.fieldMapping import lbsnPost,lbsnPlace,lbsnUser,lbsnPostReaction  
import pandas as pd
import datetime

def import_config():
    import config
    username = getattr(config, 'dbUser', 0)
    userpw = getattr(config, 'dbPassword', 0)
    return username,userpw
    
def main():

    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    # Set Output to Replace in case of encoding issues (console/windows)
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), sys.stdout.encoding, 'replace')
    # Load Config
    # will be overwritten if args are given
    input_username,input_userpw = import_config()
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('-pO', "--passwordOutput", default=0) 
    parser.add_argument('-uO', "--usernameOutput", default="postgres")
    parser.add_argument('-aO', "--serveradressOutput", default="141.76.19.66")
    parser.add_argument('-nO', "--dbnameOutput", default="lbsn_test")
    parser.add_argument('-pI', "--passwordInput", default=input_userpw) 
    parser.add_argument('-uI', "--usernameInput", default=input_username)
    parser.add_argument('-aI', "--serveradressInput", default="141.30.243.72") 
    parser.add_argument('-nI', "--dbnameInput", default="twitter-europe")    
    parser.add_argument('-t', "--transferlimit", default=0)
    parser.add_argument('-tR', "--transferReactions", default=0)
    parser.add_argument('-tG', "--transferNotGeotagged", default=0) 
    args = parser.parse_args()
    
    transferlimit = args.transferlimit
    # We're dealing with Twitter, lets create the OriginID globally
    # this OriginID is required for all CompositeKeys
    origin = lbsnOrigin()
    origin.origin_id = lbsnOrigin.TWITTER
    
    outputConnection = dbConnection(args.serveradressOutput,
                                   args.dbnameOutput,
                                   args.usernameOutput,
                                   args.passwordOutput
                                   )
    conn_output, cursor_output = outputConnection.connect()
    cursor_output.close()
    inputConnection = dbConnection(args.serveradressInput,
                                   args.dbnameInput,
                                   args.usernameInput,
                                   args.passwordInput,
                                   True # ReadOnly Mode
                                   )
    conn_input, cursor_input = inputConnection.connect()
    records,returnedRecord_count = fetchJsonData_from_LBSN(cursor_input)
    x=0
    if returnedRecord_count == 0:
        print("All fetched.")
    else:
        for record in records:
            parseJsonRecord(record, origin)
            x+=1
            if x>100:
                break
        # print(records[0])
    cursor_input.close()    

def fetchJsonData_from_LBSN(cursor, startID = 0):
    query_sql = '''
            SELECT * FROM public."input"
            WHERE in_id > %s
            ORDER BY in_id ASC LIMIT 10;
            '''
    cursor.execute(query_sql,(startID,))
    records = cursor.fetchall()
    return records, cursor.rowcount

def parseJsonRecord(JsonRecord,origin):    
    log = logging.getLogger()
    #print(JsonRecord[2])
    jsonString = JsonRecord[2]
    dbRowNumber = JsonRecord[0]
    post_guid = jsonString.get('id_str')
    postGeoaccuracy = None
    
    if not post_guid:
        sys.exit("No PostGuid")
        
    #Some preprocessing for all types:
    post_coordinates = jsonString.get('coordinates') 
    if not post_coordinates:
        #print("No Coordinates")
        l_lng = 0 
        l_lat = 0
    else:
        l_lng = post_coordinates.get('coordinates')[0]
        l_lat = post_coordinates.get('coordinates')[1]
        postGeoaccuracy = lbsnPost.LATLNG
    
    #Check if Place is mentioned
    place = jsonString.get('place')
    if place:
        placeID = place.get('id')
        bounding_box_points = place.get('bounding_box').get('coordinates')[0]
        limYMin,limYMax,limXMin,limXMax = helperFunctions.getRectangleBounds(bounding_box_points)
        bound_points_shapely = geometry.MultiPoint([(limXMin, limYMin), (limXMax, limYMax)])
        lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
        lat_center = bound_points_shapely.centroid.coords[0][1]
        place_type = place.get('place_type')
        if place_type == "country":
            #country_guid
            placeRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCountry(),placeID,origin)
            if not postGeoaccuracy:
                postGeoaccuracy = lbsnPost.COUNTRY      
            log.debug("country/admin")     
            #sys.exit("COUNTRY DETECTED - should not exist")   #debug  
        if place_type == "city" or place_type == "neighborhood" or place_type  == "admin":
            #city_guid
            placeRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCity(),place.get('id'),origin)
            if not postGeoaccuracy:
                postGeoaccuracy = lbsnPost.CITY  
            log.debug("city/neighborhood")
        if place_type == "poi":
            #place_guid
            placeRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPlace(),place.get('id'),origin)
            if not postGeoaccuracy:
                postGeoaccuracy = lbsnPost.PLACE         
            print("place/poi")
            
        placeRecord.name = place.get('name')
        placeRecord.url = place.get('url')   
        placeRecord.geom_center = "POINT(%s %s)" % (lon_center,lat_center)
        placeRecord.geom_area = Polygon(bounding_box_points).wkt # prints: 'POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))'
        if not place_type == "country":
            refCountryRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCountry(),place.get('country_code'),origin)
            refCountryRecord.name = place.get('country') # Needs to be saved        
            placeRecord.country_pkey.CopyFrom(refCountryRecord) ##Assignment Error!
        print(placeRecord)
    # Get Post/Reaction Details of user
    userRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnUser(),jsonString.get('user').get('id_str'),origin)
    # get additional information about the user, if available
    userRecord.user_fullname = jsonString.get('user').get('name')
    userRecord.follows = jsonString.get('user').get('friends_count')
    userRecord.followed = jsonString.get('user').get('followers_count')
    userBio = jsonString.get('user').get('description')
    if userBio:
        userRecord.biography = userBio
    userRecord.user_name = jsonString.get('user').get('screen_name')
    userRecord.group_count = jsonString.get('user').get('listed_count')
    userRecord.post_count = jsonString.get('user').get('statuses_count')
    userRecord.url = f'https://twitter.com/intent/user?user_id={userRecord.user_pkey.id}'
    userLanguage = helperFunctions.createNewLBSNRecord_with_id(Language(),jsonString.get('user').get('lang'),origin)
    userRecord.user_language.CopyFrom(userLanguage)
    userLocation = jsonString.get('user').get('location')
    if userLocation:
        userRecord.user_location = userLocation
    userRecord.liked_count = jsonString.get('user').get('favourites_count')
    userRecord.active_since.CopyFrom(helperFunctions.parseJSONDateStringToProtoBuf(jsonString.get('user').get('created_at'))) 
    userRecord.profile_image_url = jsonString.get('user').get('profile_image_url')
                    
    # Assignment Step
    # check first if post is reaction to other post
    # reaction means: reduced structure compared to post
    postReaction = helperFunctions.isPostReaction_Type(jsonString, True)
    if postReaction:
        reaction_guid=post_guid
        postReactionRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPostReaction(),reaction_guid,origin)
        postReactionRecord.user_pkey.CopyFrom(userRecord.user_pkey)
        postReactionRecord.reaction_latlng = "POINT(%s %s)" % (l_lng,l_lat)
        postReactionRecord.reaction_date.CopyFrom(helperFunctions.parseJSONDateStringToProtoBuf(jsonString.get('created_at'))) 
        postReactionRecord.reaction_like_count = jsonString.get('favorite_count')
        postReactionRecord.reaction_content = jsonString.get('text')
        postReactionRecord.reaction_type = postReaction.reaction_type
        if postReaction.reaction_type == lbsnPostReaction.REPLY:
            refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonString.get('in_reply_to_status_id_str'),origin)
            refUserRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnUser(),jsonString.get('in_reply_to_user_id_str'),origin)
            refUserRecord.user_name = jsonString.get('in_reply_to_screen_name') # Needs to be saved
            postReactionRecord.referencedPost_pkey.CopyFrom(refPostRecord.post_pkey) 
        elif postReaction.reaction_type == lbsnPostReaction.QUOTE:
            refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonString.get('quoted_status_id_str'),origin)
            postReactionRecord.referencedPost_pkey.CopyFrom(refPostRecord.post_pkey) 
        elif postReaction.reaction_type  == lbsnPostReaction.SHARE:
            refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonString.get('retweeted_status').get('id_str'),origin)
            postReactionRecord.referencedPost_pkey.CopyFrom(refPostRecord.post_pkey)
        # ToDo: if a Reaction refers to another reaction (Information Spread)
        # This information is currently not [available from Twitter](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object):
        # "Note that retweets of retweets do not show representations of the intermediary retweet [...]"
        # postReactionRecord.referencedPostreaction_pkey.CopyFrom(refPostReactionRecord)    
        print(postReactionRecord)
        
    else:
        # if record is a post   
        postRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),post_guid,origin)
        #hashtags = []    
        hashtags_json = jsonString.get('entities').get('hashtags')
        for hashtag in hashtags_json:    #iterate over the list
            postRecord.hashtags.append(hashtag["text"])
        postRecord.post_body = jsonString.get('text')
        postRecord.input_source = helperFunctions.cleanhtml(jsonString.get('source'))
        postRecord.post_publish_date.CopyFrom(helperFunctions.parseJSONDateStringToProtoBuf(jsonString.get('created_at'))) 
        postRecord.post_geoaccuracy = postGeoaccuracy
        postRecord.user_pkey.CopyFrom(userRecord.user_pkey)
        postRecord.post_latlng = "POINT(%s %s)" % (l_lng,l_lat)
        valueCount = lambda x: 0 if x is None else x
        postRecord.post_quote_count = valueCount(jsonString.get('quote_count'))
        postRecord.post_reply_count = valueCount(jsonString.get('reply_count'))
        postRecord.post_share_count = valueCount(jsonString.get('retweet_count'))
        postRecord.post_like_count = valueCount(jsonString.get('favorite_count'))
        postRecord.post_url = f'https://twitter.com/statuses/{post_guid}'
        postType = helperFunctions.isPost_Type(jsonString)
        if postType:
            postRecord.post_type = postType.post_type
        else:
            postRecord.post_type = lbsnPost.OTHER
            print(jsonString.get('entities').get('media'))
        postLanguage = helperFunctions.createNewLBSNRecord_with_id(Language(),jsonString.get('lang'),origin)
        postRecord.post_language.CopyFrom(postLanguage)
        postRecord.emoji.extend(helperFunctions.extract_emojis(jsonString.get('text')))
        userMentions_json = jsonString.get('entities').get('user_mentions')
        for userMention in userMentions_json:    #iterate over the list
            refUserRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnUser(),userMention.get('id_str'),origin)
            refUserRecord.user_name = userMention.get('name') # Needs to be saved
            postRecord.user_mentions_pkey.append(refUserRecord.user_pkey)
        print(postRecord)
    print(userRecord)
        
    print('\n')
    
if __name__ == "__main__":
    main()
    

    
