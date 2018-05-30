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
    if returnedRecord_count == 0:
        print("All fetched.")
    else:
        for record in records:
            parseJsonRecord(record, origin)
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
    
    jsonString = JsonRecord[2]
    dbRowNumber = JsonRecord[0]
    post_guid = jsonString.get('id_str')
    
    if not post_guid:
        print("No PostGuid")
        
    #Some preprocessing for all types:
    post_coordinates = jsonString.get('coordinates') 
    if not post_coordinates:
        #print("No Coordinates")
        l_lng = 0 
        l_lat = 0
    else:
        l_lng = post_coordinates.get('coordinates')[0]
        l_lat = post_coordinates.get('coordinates')[1]
    
    #Check if Place is mentioned
    place = jsonString.get('place')
    if place:
        bounding_box_points = place.get('bounding_box').get('coordinates')[0]
        limYMin,limYMax,limXMin,limXMax = helperFunctions.getRectangleBounds(bounding_box_points)
        bound_points_shapely = geometry.MultiPoint([(limXMin, limYMin), (limXMax, limYMax)])
        lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
        lat_center = bound_points_shapely.centroid.coords[0][1]
        place_type = place.get('place_type')
        
        # create the CompositeKey for place record 
        # from Origin and API GUID
        #placeKey = CompositeKey()
        #placeKey.origin.CopyFrom(origin)
        #placeKey.id = place.get('id')
        if place_type == "city" or place_type == "neighborhood":
            #city_guid
            cityRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCity(),place.get('id'),origin)
            cityRecord.name = place.get('name')
            cityRecord.url = place.get('url')
            refCountryRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCountry(),place.get('country_code'),origin)
            cityRecord.country_pkey.CopyFrom(refCountryRecord)
            cityRecord.geom_center = "POINT(%s %s)" % (lon_center,lat_center)
            cityRecord.geom_area = Polygon(bounding_box_points).wkt # prints: 'POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))'
            print(cityRecord)
            log.debug("city/neighborhood")
        if place_type == "country" or place_type  == "admin":
            #country_guid
            log.debug("country/admin") 
        if place_type == "poi":
            #place_guid
            print("place/poi")
            
    # Assignment Step
    # check first if post is reaction to other post
    # reaction means: reduced structure compared to post
    postReaction = helperFunctions.isPostReaction_Type(jsonString, True)
    if postReaction:
        reaction_guid=post_guid
        postReactionRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPostReaction(),reaction_guid,origin)
        refUserRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnUser(),jsonString.get('user').get('id_str'),origin)
        postReactionRecord.user_pkey.CopyFrom(refUserRecord.user_pkey)
        postReactionRecord.reaction_latlng = "POINT(%s %s)" % (l_lng,l_lat)
        # Parse String -Timestamp Format found in Twitter json
        created_at = datetime.datetime.strptime(jsonString.get('created_at'),'%a %b %d %H:%M:%S +0000 %Y') 
        timestampRecord = Timestamp()
        # Convert to ProtoBuf Timestamp Recommendation
        timestampRecord.FromDatetime(created_at)
        postReactionRecord.reaction_date.CopyFrom(timestampRecord)
        postReactionRecord.reaction_like_count = jsonString.get('favorite_count')
        postReactionRecord.reaction_content = jsonString.get('text')
        postReactionRecord.post_type = postReaction.post_type
        if postReaction.post_type == lbsnPostReaction.REPLY:
            refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonString.get('in_reply_to_status_id_str'),origin)
            postReactionRecord.post_pkey.CopyFrom(refPostRecord.post_pkey) 
        elif isinstance(postReaction.post_type,lbsnPostReaction.QUOTE):
            refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonString.get('quoted_status_id_str'),origin)
            postReactionRecord.post_pkey.CopyFrom(refPostRecord) 
        elif isinstance(postReaction.post_type,lbsnPostReaction.SHARE):
            refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonString.get('retweeted_status').get('id_str'),origin)
            postReactionRecord.post_pkey.CopyFrom(refPostRecord)
        print(postReactionRecord)
    else:
        hashtags = []    
        hashtags_json = jsonString.get('entities').get('hashtags')
        for hashtag in hashtags_json:    #iterate over the list
            hashtags.append(hashtag["text"])
        record = lbsnPost(post_guid = post_guid, 
                        post_body=jsonString.get('text'),
                        input_source=helperFunctions.cleanhtml(jsonString.get('source')),
                        post_publish_date=jsonString.get('created_at'),
                        user_guid=jsonString.get('user').get('id_str'), 
                        post_latlng_WKT="POINT(%s %s)" % (l_lng,l_lat),
                        post_quote_count=jsonString.get('quote_count'),
                        post_comment_count=jsonString.get('reply_count'),                 
                        post_share_count=jsonString.get('retweet_count'), 
                        post_like_count=jsonString.get('favorite_count'),
                        hashtags=hashtags,
                        post_type=jsonString.get('entities').get('media'),              
                        post_language=jsonString.get('lang'),
                        emoji=helperFunctions.extract_emojis(jsonString.get('text'))
                        )
    print('\n')
    record.attr_list(True)
    
if __name__ == "__main__":
    main()
    

    
