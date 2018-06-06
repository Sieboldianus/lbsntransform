# -*- coding: utf-8 -*-

from classes.helperFunctions import helperFunctions
from classes.helperFunctions import lbsnRecordDicts as lbsnRecordDicts
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import shapely.geometry as geometry
from shapely.geometry.polygon import Polygon
import logging 

class fieldMappingTwitter():  
    def parseJsonRecord(jsonStringDict,origin,lbsnRecords):    
        log = logging.getLogger('__main__')#logging.getLogger()
        # log.debug(jsonStringDict)
        # Define Sets that will hold unique values of each lbsn type
        
        post_guid = jsonStringDict.get('id_str')
        #log.debug(f'\n\n##################### {post_guid} #####################')
        postGeoaccuracy = None
        
        if not post_guid:
            log.warning(f'No PostGuid\n\n{jsonStringDict}')
            input("Press Enter to continue...")
    
        # Get Post/Reaction Details of User
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
        userRecord.url = f'https://twitter.com/intent/user?user_id={userRecord.pkey.id}'
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
                    
        # Some preprocessing for all types:
        post_coordinates = jsonStringDict.get('coordinates') 
        if not post_coordinates:
            l_lng = 0 
            l_lat = 0
        else:
            l_lng = post_coordinates.get('coordinates')[0]
            l_lat = post_coordinates.get('coordinates')[1]
            postGeoaccuracy = lbsnPost.LATLNG
        
        # Check if Place is mentioned
        place = jsonStringDict.get('place')
        if place:
            placeID = place.get('id')
            #if not placeID:
            #    sys.exit(print(jsonStringDict))
            bounding_box_points = place.get('bounding_box').get('coordinates')[0]
            limYMin,limYMax,limXMin,limXMax = helperFunctions.getRectangleBounds(bounding_box_points)
            bound_points_shapely = geometry.MultiPoint([(limXMin, limYMin), (limXMax, limYMax)])
            lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
            lat_center = bound_points_shapely.centroid.coords[0][1]
            place_type = place.get('place_type')
            if place_type == "country":
                # country_guid
                # in case of country, we do not need to save the GUID from Twitter - country_code is already unique
                placeRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCountry(),place.get('country_code'),origin)
                if not postGeoaccuracy:
                    postGeoaccuracy = lbsnPost.COUNTRY      
                #log.debug(f'Placetype detected: country')
            elif place_type in ("city","neighborhood","admin"):
                # city_guid
                placeRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCity(),place.get('id'),origin)
                if not postGeoaccuracy or postGeoaccuracy == lbsnPost.COUNTRY:
                    postGeoaccuracy = lbsnPost.CITY  
                    l_lng = lon_center
                    l_lat = lat_center
                # log.debug(f'Placetype detected: city/neighborhood/admin')
            elif place_type == "poi":
                # place_guid
                # For POIs, City is not available on Twitter
                placeRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPlace(),place.get('id'),origin)
                if not postGeoaccuracy or postGeoaccuracy == lbsnPost.CITY:
                    postGeoaccuracy = lbsnPost.PLACE  
                    l_lng = lon_center
                    l_lat = lat_center
            else:
                log.warning(f'No Place Type Detected: {jsonStringDict}')                 
                # log.debug(f'Placetype detected: place/poi')
            # At the moment, English name are the main references; all other language specific references are stored in name_alternatives
            # Bugfix necessary: some English names get still saved as name_alternatives
            if not userRecord.user_language.language_short or userRecord.user_language.language_short in ('en','und'):
                placeRecord.name = place.get('name')
            else:
                alt_name = place.get('name')              
                placeRecord.name_alternatives.append(alt_name)
            placeRecord.url = place.get('url')
            placeRecord.geom_center = "POINT(%s %s)" % (lon_center,lat_center)
            placeRecord.geom_area = Polygon(bounding_box_points).wkt # prints: 'POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))'
            if isinstance(placeRecord,lbsnCity):
                refCountryRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCountry(),place.get('country_code'),origin)
                # At the moment, only English name references are processed
                if not userRecord.user_language.language_short or userRecord.user_language.language_short in ('en','und'):
                    refCountryRecord.name = place.get('country') # Needs to be saved 
                else:
                    alt_name = place.get('country')
                    refCountryRecord.name_alternatives.append(alt_name)
                lbsnRecords.AddRecordsToDict(refCountryRecord)
                placeRecord.country_pkey.CopyFrom(refCountryRecord.pkey)
            # log.debug(f'Final Place Record: {placeRecord}')
            lbsnRecords.AddRecordsToDict(placeRecord)
        
        # First process attributes that are similar for posts and reactions
        # Get User Mentions
        # This User List needs to be saved separately
        isTruncated = jsonStringDict.get('truncated')
        if isTruncated:
            userMentionsJson = jsonStringDict.get('extended_tweet').get('entities').get('user_mentions')
        else:
            userMentionsJson = jsonStringDict.get('entities').get('user_mentions')
        refUserRecords = helperFunctions.getMentionedUsers(userMentionsJson,origin)
        # log.debug(f'User mentions: {refUserRecords}')
        lbsnRecords.AddRecordsToDict(refUserRecords)  
        # Assignment Step
        # check first if post is reaction to other post
        # reaction means: reduced structure compared to post
        postReaction = helperFunctions.isPostReaction_Type(jsonStringDict, True)
        if postReaction:
            reaction_guid=post_guid
            postReactionRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPostReaction(),reaction_guid,origin)
            postReactionRecord.user_pkey.CopyFrom(userRecord.pkey)
            postReactionRecord.reaction_latlng = "POINT(%s %s)" % (l_lng,l_lat)
            postReactionRecord.reaction_date.CopyFrom(helperFunctions.parseJSONDateStringToProtoBuf(jsonStringDict.get('created_at'))) 
            postReactionRecord.reaction_like_count = jsonStringDict.get('favorite_count')
            postReactionRecord.reaction_content = jsonStringDict.get('text')
            postReactionRecord.reaction_type = postReaction.reaction_type
            if postReaction.reaction_type == lbsnPostReaction.REPLY:
                refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonStringDict.get('in_reply_to_status_id_str'),origin)
                refUserRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnUser(),jsonStringDict.get('in_reply_to_user_id_str'),origin)
                refUserRecord.user_name = jsonStringDict.get('in_reply_to_screen_name') # Needs to be saved
            elif postReaction.reaction_type == lbsnPostReaction.QUOTE:
                refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonStringDict.get('quoted_status_id_str'),origin)
            elif postReaction.reaction_type  == lbsnPostReaction.SHARE:
                refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonStringDict.get('retweeted_status').get('id_str'),origin)
            postReactionRecord.referencedPost_pkey.CopyFrom(refPostRecord.pkey)
            # ToDo: if a Reaction refers to another reaction (Information Spread)
            # This information is currently not [available from Twitter](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object):
            # "Note that retweets of retweets do not show representations of the intermediary retweet [...]"
            # postReactionRecord.referencedPostreaction_pkey.CopyFrom(refPostReactionRecord)    
            #log.debug(f'Reaction record: {postReactionRecord}')
            lbsnRecords.AddRecordsToDict(postReactionRecord)  
        else:
            # if record is a post   
            postRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),post_guid,origin)  
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
            postRecord.user_pkey.CopyFrom(userRecord.pkey)
            postRecord.post_latlng = "POINT(%s %s)" % (l_lng,l_lat)
            if place:
                try:
                    refCountryRecord
                    if refCountryRecord:
                        postRecord.country_pkey.CopyFrom(refCountryRecord.pkey)
                except NameError:
                    pass
                if place_type == "country":
                    postRecord.country_pkey.CopyFrom(placeRecord.pkey) 
                if place_type in ("city","neighborhood","admin"):
                    postRecord.city_pkey.CopyFrom(placeRecord.pkey)
                elif place_type == "poi":
                    postRecord.place_pkey.CopyFrom(placeRecord.pkey)
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
                #log.debug(f'Other Post type detected: {jsonStringDict.get("entities").get("media")}')
            refPostLanguage = Language()
            refPostLanguage.language_short = jsonStringDict.get('lang')
            postRecord.post_language.CopyFrom(refPostLanguage)
            postRecord.emoji.extend(helperFunctions.extract_emojis(jsonStringDict.get('text')))
            # Add mentioned userRecords
            postRecord.user_mentions_pkey.extend([userRef.pkey for userRef in refUserRecords])  
            # because standard print statement will produce escaped text, we can use protobuf text_format to give us a human friendly version of the text
            # log.debug(f'Post record: {text_format.MessageToString(postRecord,as_utf8=True)}')
            # log.debug(f'Post record: {postRecord}')
            lbsnRecords.AddRecordsToDict(postRecord) 
        # log.debug(f'The user who posted/reacted: {userRecord}')
        lbsnRecords.AddRecordsToDict(userRecord)
        
        return lbsnRecords      