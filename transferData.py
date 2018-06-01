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
from google.protobuf import text_format

def import_config():
    import config
    username = getattr(config, 'dbUser', 0)
    userpw = getattr(config, 'dbPassword', 0)
    return username,userpw
    
def main():


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
    parser.add_argument('-d', "--debugMode", default="INFO") #needs to be implemented
    args = parser.parse_args()
    logging.basicConfig(handlers=[logging.FileHandler('test.log', 'w', 'utf-8')],
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    log = logging.getLogger(__name__)
    # Get Stream handler, so we can also print to console while logging to file
    logging.getLogger().addHandler(logging.StreamHandler())
        
    transferlimit = int(args.transferlimit)
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
    processedRecords = 0
    conn_input, cursor_input = inputConnection.connect()
    finished = False
    while not finished:
        records,returnedRecord_count = fetchJsonData_from_LBSN(cursor_input)
        if returnedRecord_count == 0:
            finished = True
            log.info(f'Processed all available {processedRecords} records. Done.')
        else:
            for record in records:
                dbRowNumber = record[0]
                #singleUJSONRecord = ujson.loads(record[2])
                singleJSONRecordDict = record[2]
                parseJsonRecord(singleJSONRecordDict, origin)
                processedRecords += 1
                if processedRecords >= transferlimit:
                    finished = True
                    log.info(f'Processed {processedRecords} records. Done.')
                    break
            # print(records[0])
    cursor_input.close()    

def fetchJsonData_from_LBSN(cursor, startID = 0):
    query_sql = '''
            SELECT in_id,insert_time,data::json FROM public."input"
            WHERE in_id > %s
            ORDER BY in_id ASC LIMIT 10;
            '''
    cursor.execute(query_sql,(startID,))
    records = cursor.fetchall()
    return records, cursor.rowcount

def parseJsonRecord(jsonStringDict,origin):    
    log = logging.getLogger()
    #log.debug(jsonStringDict)
    
    post_guid = jsonStringDict.get('id_str')
    log.debug(f'\n\n##################### {post_guid} #####################')
    postGeoaccuracy = None
    
    if not post_guid:
        sys.exit("No PostGuid")
        
    #Some preprocessing for all types:
    post_coordinates = jsonStringDict.get('coordinates') 
    if not post_coordinates:
        #print("No Coordinates")
        l_lng = 0 
        l_lat = 0
    else:
        l_lng = post_coordinates.get('coordinates')[0]
        l_lat = post_coordinates.get('coordinates')[1]
        postGeoaccuracy = lbsnPost.LATLNG
    
    #Check if Place is mentioned
    place = jsonStringDict.get('place')
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
            log.debug(f'Placetype detected: country/')     
            #sys.exit("COUNTRY DETECTED - should not exist")   #debug  
        if place_type == "city" or place_type == "neighborhood" or place_type  == "admin":
            #city_guid
            placeRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCity(),place.get('id'),origin)
            if not postGeoaccuracy or postGeoaccuracy == lbsnPost.COUNTRY:
                postGeoaccuracy = lbsnPost.CITY  
                l_lng = lon_center
                l_lat = lat_center
            log.debug(f'Placetype detected: city/neighborhood/admin')
        if place_type == "poi":
            #place_guid
            placeRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPlace(),place.get('id'),origin)
            if not postGeoaccuracy or postGeoaccuracy == lbsnPost.CITY:
                postGeoaccuracy = lbsnPost.PLACE  
                l_lng = lon_center
                l_lat = lat_center                       
            log.debug(f'Placetype detected: place/poi')
            
        placeRecord.name = place.get('name')
        placeRecord.url = place.get('url')   
        placeRecord.geom_center = "POINT(%s %s)" % (lon_center,lat_center)
        placeRecord.geom_area = Polygon(bounding_box_points).wkt # prints: 'POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))'
        if not place_type == "country":
            refCountryRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCountry(),place.get('country_code'),origin)
            refCountryRecord.name = place.get('country') # Needs to be saved        
            placeRecord.country_pkey.CopyFrom(refCountryRecord) ##Assignment Error!
        log.debug(f'Final Place Record: {placeRecord}')
    # Get Post/Reaction Details of user
    userRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnUser(),jsonStringDict.get('user').get('id_str'),origin)
    # get additional information about the user, if available
    userRecord.user_fullname = jsonStringDict.get('user').get('name')
    userRecord.follows = jsonStringDict.get('user').get('friends_count')
    userRecord.is_private = jsonStringDict.get('user').get('protected')
    userRecord.followed = jsonStringDict.get('user').get('followers_count')
    userBio = jsonStringDict.get('user').get('description')
    if userBio:
        userRecord.biography = userBio
    userRecord.user_name = jsonStringDict.get('user').get('screen_name')
    userRecord.group_count = jsonStringDict.get('user').get('listed_count')
    userRecord.post_count = jsonStringDict.get('user').get('statuses_count')
    userRecord.url = f'https://twitter.com/intent/user?user_id={userRecord.user_pkey.id}'
    refUserLanguage = Language()
    refUserLanguage.language_short = jsonStringDict.get('user').get('lang')
    userRecord.user_language.CopyFrom(refUserLanguage)    
    userLocation = jsonStringDict.get('user').get('location')
    if userLocation:
        userRecord.user_location = userLocation
    userRecord.liked_count = jsonStringDict.get('user').get('favourites_count')
    userRecord.active_since.CopyFrom(helperFunctions.parseJSONDateStringToProtoBuf(jsonStringDict.get('user').get('created_at'))) 
    userProfileImageURL = jsonStringDict.get('user').get('profile_image_url')
    if not userProfileImageURL == "http://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png":
        userRecord.profile_image_url = userProfileImageURL
    
    # First process attributes that are similar for posts and reactions
    # Get User Mentions
    # This User List needs to be saved separately
    isTruncated = jsonStringDict.get('truncated')
    if isTruncated:
        userMentionsJson = jsonStringDict.get('extended_tweet').get('entities').get('user_mentions')
    else:
        userMentionsJson = jsonStringDict.get('entities').get('user_mentions')
    refUserRecords = helperFunctions.getMentionedUsers(userMentionsJson,origin)
    log.debug(f'User mentions: {refUserRecords}')
    
    # Assignment Step
    # check first if post is reaction to other post
    # reaction means: reduced structure compared to post
    postReaction = helperFunctions.isPostReaction_Type(jsonStringDict, True)
    if postReaction:
        reaction_guid=post_guid
        postReactionRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPostReaction(),reaction_guid,origin)
        postReactionRecord.user_pkey.CopyFrom(userRecord.user_pkey)
        postReactionRecord.reaction_latlng = "POINT(%s %s)" % (l_lng,l_lat)
        postReactionRecord.reaction_date.CopyFrom(helperFunctions.parseJSONDateStringToProtoBuf(jsonStringDict.get('created_at'))) 
        postReactionRecord.reaction_like_count = jsonStringDict.get('favorite_count')
        postReactionRecord.reaction_content = jsonStringDict.get('text')
        postReactionRecord.reaction_type = postReaction.reaction_type
        if postReaction.reaction_type == lbsnPostReaction.REPLY:
            refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonStringDict.get('in_reply_to_status_id_str'),origin)
            refUserRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnUser(),jsonStringDict.get('in_reply_to_user_id_str'),origin)
            refUserRecord.user_name = jsonStringDict.get('in_reply_to_screen_name') # Needs to be saved
            postReactionRecord.referencedPost_pkey.CopyFrom(refPostRecord.post_pkey) 
        elif postReaction.reaction_type == lbsnPostReaction.QUOTE:
            refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonStringDict.get('quoted_status_id_str'),origin)
            postReactionRecord.referencedPost_pkey.CopyFrom(refPostRecord.post_pkey) 
        elif postReaction.reaction_type  == lbsnPostReaction.SHARE:
            refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonStringDict.get('retweeted_status').get('id_str'),origin)
            postReactionRecord.referencedPost_pkey.CopyFrom(refPostRecord.post_pkey)
        # ToDo: if a Reaction refers to another reaction (Information Spread)
        # This information is currently not [available from Twitter](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object):
        # "Note that retweets of retweets do not show representations of the intermediary retweet [...]"
        # postReactionRecord.referencedPostreaction_pkey.CopyFrom(refPostReactionRecord)    
        log.debug(f'Reaction record: {postReactionRecord}')
        
    else:
        # if record is a post   
        postRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),post_guid,origin)
        #hashtags = []    
        if isTruncated:
            postRecord.post_body = jsonStringDict.get('extended_tweet').get('full_text')
            hashtags_json = jsonStringDict.get('extended_tweet').get('entities').get('hashtags')
        else:
            postRecord.post_body = jsonStringDict.get('text')
            hashtags_json = jsonStringDict.get('entities').get('hashtags')
        for hashtag in hashtags_json:    #iterate over the list
            postRecord.hashtags.append(hashtag["text"])            
        postRecord.input_source = helperFunctions.cleanhtml(jsonStringDict.get('source'))
        postRecord.post_publish_date.CopyFrom(helperFunctions.parseJSONDateStringToProtoBuf(jsonStringDict.get('created_at'))) 
        postRecord.post_geoaccuracy = postGeoaccuracy
        postRecord.user_pkey.CopyFrom(userRecord.user_pkey)
        postRecord.post_latlng = "POINT(%s %s)" % (l_lng,l_lat)
        valueCount = lambda x: 0 if x is None else x
        postRecord.post_quote_count = valueCount(jsonStringDict.get('quote_count'))
        postRecord.post_reply_count = valueCount(jsonStringDict.get('reply_count'))
        postRecord.post_share_count = valueCount(jsonStringDict.get('retweet_count'))
        postRecord.post_like_count = valueCount(jsonStringDict.get('favorite_count'))
        postRecord.post_url = f'https://twitter.com/statuses/{post_guid}'
        postType = helperFunctions.isPost_Type(jsonStringDict)
        if postType:
            postRecord.post_type = postType.post_type
        else:
            postRecord.post_type = lbsnPost.OTHER
            log.debug(f'Other Post type detected: {jsonStringDict.get("entities").get("media")}')
        refPostLanguage = Language()
        refPostLanguage.language_short = jsonStringDict.get('lang')
        postRecord.post_language.CopyFrom(refPostLanguage)
        postRecord.emoji.extend(helperFunctions.extract_emojis(jsonStringDict.get('text')))
        # Add mentioned userRecords
        postRecord.user_mentions_pkey.extend([userRef.user_pkey for userRef in refUserRecords])  
        # because standard print statement will produce escaped text, we can use protobuf text_format to give us a human friendly version of the text
        log.debug(f'Post record: {text_format.MessageToString(postRecord,as_utf8=True)}')
    log.debug(f'The user who posted/reacted: {userRecord}')
    
if __name__ == "__main__":
    main()
    

    
