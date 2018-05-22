# -*- coding: utf-8 -*-

import getpass
import argparse
import logging 
from classes.dbConnection import dbConnection
from classes.helperFunctions import helperFunctions
import io
import sys
import shapely.geometry as geometry
from shapely.geometry.polygon import Polygon
from classes.fieldMapping import lbsnPost,lbsnPlace,lbsnUser,lbsnPostReaction  
import pandas as pd

def main():
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    #Set Output to Replace in case of encoding issues (console/windows)
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), sys.stdout.encoding, 'replace')
    #Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('-pO', "--passwordOutput", default=0) 
    parser.add_argument('-uO', "--usernameOutput", default="postgres")
    parser.add_argument('-aO', "--serveradressOutput", default="141.76.19.66")
    parser.add_argument('-nO', "--dbnameOutput", default="lbsn_test")
    parser.add_argument('-pI', "--passwordInput", default=0) 
    parser.add_argument('-uI', "--usernameInput", default="alex")
    parser.add_argument('-aI', "--serveradressInput", default="141.30.243.72") 
    parser.add_argument('-nI', "--dbnameInput", default="twitter-europe")    
    parser.add_argument('-t', "--transferlimit", default=0)
    parser.add_argument('-tR', "--transferReactions", default=0)
    parser.add_argument('-tG', "--transferNotGeotagged", default=0) 
    args = parser.parse_args()
    
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
            parseJsonRecord(record)
        #print(records[0])
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

def parseJsonRecord(JsonRecord):
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
        if place_type == "city" or place_type == "neighborhood":
            #city_guid
            placeRecord = lbsnPlace(country_guid = place.get('country_code'),
                            city_guid = place.get('id'),
                            city_name = place.get('name'),
                            place_url = place.get('url'),
                            geom_center = "POINT(%s %s)" % (lon_center,lat_center),
                            geom_area = Polygon(bounding_box_points).wkt # prints: 'POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))'
                            )
            placeRecord.attr_list(True)
            print("city/neighborhood")
        if place_type == "country" or place_type  == "admin":
            #country_guid
            print("country/admin") 
        if place_type == "poi":
            #place_guid
            print("place/poi")
            
    #Assignment Step
    if jsonString.get('in_reply_to_status_id_str'):
        record = lbsnPostReaction(reaction_type = "reply",
                        reaction_guid=post_guid, 
                        post_guid=jsonString.get('in_reply_to_status_id_str'),
                        user_guid=jsonString.get('user').get('id_str'), 
                        reaction_latlng_WKT="POINT(%s %s)" % (l_lng,l_lat),
                        reaction_date=jsonString.get('created_at'),
                        reaction_content=jsonString.get('text'),
                        reaction_like_count= jsonString.get('favorite_count')
                        )        
    elif jsonString.get('quoted_status_id_str'):
        record = lbsnPostReaction(reaction_type = "quote",
                        reaction_guid=post_guid, 
                        post_guid=jsonString.get('quoted_status_id_str'),
                        user_guid=jsonString.get('user').get('id_str'), 
                        reaction_latlng_WKT="POINT(%s %s)" % (l_lng,l_lat),
                        reaction_date=jsonString.get('created_at'),
                        reaction_content=jsonString.get('text'),
                        reaction_like_count= jsonString.get('favorite_count')
                        )        
    elif jsonString.get('retweeted_status'):
        record = lbsnPostReaction(reaction_type = "share",
                        reaction_guid=post_guid, 
                        post_guid=jsonString.get('retweeted_status').get('id_str'),
                        user_guid=jsonString.get('user').get('id_str'), 
                        reaction_latlng_WKT="POINT(%s %s)" % (l_lng,l_lat),
                        reaction_date=jsonString.get('created_at'),
                        reaction_content=jsonString.get('text'),
                        reaction_like_count= jsonString.get('favorite_count')
                        )
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
    

    
