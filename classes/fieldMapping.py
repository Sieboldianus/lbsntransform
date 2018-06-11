# -*- coding: utf-8 -*-

from classes.helperFunctions import helperFunctions
from classes.helperFunctions import lbsnRecordDicts as lbsnRecordDicts
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import shapely.geometry as geometry
from shapely.geometry.polygon import Polygon
import logging
import re

class fieldMappingTwitter():
    def __init__(self, disableReactionPostReferencing = False):
        # We're dealing with Twitter in this class, lets create the OriginID globally
        # this OriginID is required for all CompositeKeys
        origin = lbsnOrigin()
        origin.origin_id = lbsnOrigin.TWITTER
        self.origin = origin
        self.lbsnRecords = lbsnRecordDicts() #this is where all the data will be stored
        self.log = logging.getLogger('__main__')#logging.getLogger()
        self.disableReactionPostReferencing = disableReactionPostReferencing

    def parseJsonRecord(self, jsonStringDict):    
        # 1. Extract all relevant Post Attributes
        #    1.a extract post coordinates
        #    1.b extract user attributes
        #    1.c extract place attributes (poi, city, neigborhood, admin, country)
        #    1.d extract extract extended tweet, if available, and extended entities, if available
        # 2. decide if post is reaction (reply, quote, share, see https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/entities-object.html)
        # 3. if post is reaction, copy reduced reaction attributes from extracted lbsnPost
        # 4. add post/reaction to recordDict
        # 5. process all referenced posts
        #    5.a Retweet(=Share) and Quote Tweets are special kinds of Tweets that contain the original Tweet as an embedded object.
        #    5.b Retweets have a top-level "retweeted_status" object, and Quoted Tweets have a "quoted_status" object
        # process tweet-post object
        postRecord = self.extractPost(jsonStringDict)
        # Assignment Step
        # check if post is reaction to other post
        # reaction means: reduced structure compared to post; 
        # reactions often include the complete original post, therefore nested processing necessary
        if helperFunctions.isPostReaction(jsonStringDict):
            postReactionRecord = self.mapPostRecord_To_PostReactionRecord(postRecord)
            if 'quoted_status' in jsonStringDict: #Quote is both: Share & Reply
                postReactionRecord.reaction_type = lbsnPostReaction.QUOTE
                refPostRecord = self.extractPost(jsonStringDict.get('quoted_status'))
            #elif 'retweeted_status' in jsonStringDict: #quoted_status_id_str 
            elif hasattr(jsonStringDict, 'retweeted_status'):
                sys.exit(jsonStringDict)
                # no retweets are available because of Geo-Tweet limitation:
                # "Note that native Retweets are not matched by this parameter. While the original Tweet may have a location, the Retweet will not"
                # see https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters.html
                postReactionRecord.reaction_type = lbsnPostReaction.SHARE 
                refPostRecord = self.extractPost(jsonStringDict.get('retweeted_status'))
            elif jsonStringDict.get('in_reply_to_status_id_str'):
                # if reply, original tweet is not available (?)
                postReactionRecord.reaction_type = lbsnPostReaction.COMMENT
                refPostRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),jsonStringDict.get('in_reply_to_status_id_str'),self.origin)
                refUserRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnUser(),jsonStringDict.get('in_reply_to_user_id_str'),self.origin)
                refUserRecord.user_name = jsonStringDict.get('in_reply_to_screen_name') # Needs to be saved
                self.lbsnRecords.AddRecordsToDict(refUserRecord)          
                refPostRecord.user_pkey.CopyFrom(refUserRecord.pkey)
            
            # add referenced post pkey to reaction    
            if not self.disableReactionPostReferencing:
                postReactionRecord.referencedPost_pkey.CopyFrom(refPostRecord.pkey)
                # ToDo: if a Reaction refers to another reaction (Information Spread)
                # This information is currently not [available from Twitter](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object):
                # "Note that retweets of retweets do not show representations of the intermediary retweet [...]"
                # would be added to. postReactionRecord.referencedPostReaction_pkey
                if refPostRecord:
                    self.lbsnRecords.AddRecordsToDict(refPostRecord)
            # add postReactionRecord to Dict        
            self.lbsnRecords.AddRecordsToDict(postReactionRecord)      
        else:
            # add postReactionRecord to Dict 
            self.lbsnRecords.AddRecordsToDict(postRecord)       
        
    def extractUser(self,jsonStringDict):
        user = jsonStringDict
        userRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnUser(),user.get('id_str'),self.origin)
        # get additional information about the user, if available
        userRecord.user_fullname = user.get('name')
        userRecord.follows = user.get('friends_count')
        userRecord.is_private = user.get('protected')
        userRecord.followed = user.get('followers_count')
        userBio = user.get('description')
        if userBio:
            userRecord.biography = userBio
        userRecord.user_name = user.get('screen_name')
        userRecord.group_count = user.get('listed_count')
        userRecord.post_count = user.get('statuses_count')
        userRecord.url = f'https://twitter.com/intent/user?user_id={userRecord.pkey.id}'
        refUserLanguage = Language()
        refUserLanguage.language_short = user.get('lang')
        userRecord.user_language.CopyFrom(refUserLanguage)    
        userLocation = user.get('location')
        if userLocation:
            userRecord.user_location = userLocation
        userRecord.liked_count = user.get('favourites_count')
        userRecord.active_since.CopyFrom(helperFunctions.parseJSONDateStringToProtoBuf(user.get('created_at'))) 
        userProfileImageURL = user.get('profile_image_url')
        if not userProfileImageURL == "http://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png":
            userRecord.profile_image_url = userProfileImageURL
        userTimezone = user.get('time_zone')
        if userTimezone:
            userRecord.user_timezone = userTimezone
        userUTCOffset = user.get('utc_offset')
        if userUTCOffset:
            userRecord.user_utc_offset = userUTCOffset
        return userRecord
          
    def extractPost(self,jsonStringDict):
        post_guid = jsonStringDict.get('id_str')
        if not post_guid:
           log.warning(f'No PostGuid\n\n{jsonStringDict}')
           input("Press Enter to continue... (entry will be skipped)")
           return None    
        #if 'retweeted_status' in jsonStringDict:
        #    sys.exit(jsonStringDict)
        postRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPost(),post_guid,self.origin) 
        postGeoaccuracy = None
        # Get Post/Reaction Details of User
        userRecord = self.extractUser(jsonStringDict.get('user'))
        self.lbsnRecords.AddRecordsToDict(userRecord)         

        # Some preprocessing for all types:
        post_coordinates = jsonStringDict.get('coordinates') 
        if post_coordinates:
            l_lng = post_coordinates.get('coordinates')[0]
            l_lat = post_coordinates.get('coordinates')[1]
            postRecord.post_geoaccuracy = lbsnPost.LATLNG
            postRecord.post_latlng = "POINT(%s %s)" % (l_lng,l_lat)
        
        # Check if Place is mentioned
        postPlace_json = jsonStringDict.get('place')
        if postPlace_json:
            # we need some information from postRecord to create placeRecord (e.g. user language, geoaccuracy, post_latlng)
            # some of the information from place will also modify postRecord attributes; therefore return both
            placeRecord, postGeoaccuracy, postCountry = self.extractPlace(postPlace_json, postRecord.post_geoaccuracy, userRecord.user_language) 
            if not postRecord.post_geoaccuracy:
                postRecord.post_geoaccuracy = postGeoaccuracy
            #postRecord.post_geoaccuracy = twitterPostAttributes.geoaccuracy 
            self.lbsnRecords.AddRecordsToDict(placeRecord)
            if postCountry:
                postRecord.country_pkey.CopyFrom(postCountry.pkey)
            if isinstance(placeRecord, lbsnCity):
                postRecord.city_pkey.CopyFrom(placeRecord.pkey)
            # either city or place, Twitter user cannot attach both (?)
            elif isinstance(placeRecord, lbsnPlace):
                postRecord.place_pkey.CopyFrom(placeRecord.pkey)      
            # substitute postRecord LatLng Coordinates from placeRecord, if not already set     
            if not postRecord.post_latlng and postGeoaccuracy in (lbsnPost.CITY,lbsnPost.PLACE):
                postRecord.post_latlng = placeRecord.geom_center
        # if still no geoinformation, send post to Null-Island
        if not postRecord.post_latlng:
            postRecord.post_latlng = "POINT(%s %s)" % (0,0)
        # Process attributes of twitter post
        postRecord.input_source = helperFunctions.cleanhtml(jsonStringDict.get('source'))
        postRecord.post_publish_date.CopyFrom(helperFunctions.parseJSONDateStringToProtoBuf(jsonStringDict.get('created_at')))
        postRecord.user_pkey.CopyFrom(userRecord.pkey)
        valueCount = lambda x: 0 if x is None else x
        postRecord.post_quote_count = valueCount(jsonStringDict.get('quote_count'))
        postRecord.post_comment_count = valueCount(jsonStringDict.get('reply_count'))
        postRecord.post_share_count = valueCount(jsonStringDict.get('retweet_count'))
        postRecord.post_like_count = valueCount(jsonStringDict.get('favorite_count'))
        postRecord.post_url = f'https://twitter.com/statuses/{post_guid}'    
        postLanguage = Language()
        postLanguage.language_short = jsonStringDict.get('lang')
        postRecord.post_language.CopyFrom(postLanguage)            
        # If Extended_tweet object is available, process entities and post_body (text) data from extended object
        isTruncated = jsonStringDict.get('truncated')
        if isTruncated:
            #if the "truncated" field is set to true, and the "extended_tweet" object provides complete "full_text" and "entities" Tweet metadata
            if 'extended_tweet' in jsonStringDict:
                jsonStringDict = jsonStringDict.get('extended_tweet') # Source for all data is extended object, if available
                postRecord.post_body = jsonStringDict.get('full_text')
            else:
                log.warning(f'Truncated but no extended_tweet: {jsonStringDict}')
                input("Press Enter to continue... (entry will be skipped)")
                return None  
        else:
            postRecord.post_body = jsonStringDict.get('text')
        #if 'RT @' in postRecord.post_body:
        #    sys.exit(jsonStringDict)
        if 'extended_entities' in jsonStringDict:
            entitiesJson = jsonStringDict.get('extended_entities')
        else:
            entitiesJson = jsonStringDict.get('entities')     
        
        hashtags_json = entitiesJson.get('hashtags')
        if hashtags_json:
            for hashtag in hashtags_json:    #iterate over the list
                postRecord.hashtags.append(hashtag["text"])
        # Look for mentioned userRecords
        userMentionsJson = entitiesJson.get('user_mentions')
        if userMentionsJson:
            refUserRecords = helperFunctions.getMentionedUsers(userMentionsJson,self.origin)
            self.lbsnRecords.AddRecordsToDict(refUserRecords)
            postRecord.user_mentions_pkey.extend([userRef.pkey for userRef in refUserRecords])         
        mediaJson = entitiesJson.get('media')
        if mediaJson:
            postRecord.post_type = helperFunctions.assignMediaPostType(mediaJson)
        else:
            postRecord.post_type = lbsnPost.TEXT
        postRecord.emoji.extend(helperFunctions.extract_emojis(postRecord.post_body))
        # because standard print statement will produce escaped text, we can use protobuf text_format to give us a human friendly version of the text
        # log.debug(f'Post record: {text_format.MessageToString(postRecord,as_utf8=True)}')
        # log.debug(f'Post record: {postRecord}')
        return postRecord
    
    def mapPostRecord_To_PostReactionRecord(self,postRecord):
        postReactionRecord = lbsnPostReaction()
        postReactionRecord.pkey.CopyFrom(postRecord.pkey)
        postReactionRecord.user_pkey.CopyFrom(postRecord.user_pkey)
        postReactionRecord.reaction_latlng = postRecord.post_latlng
        postReactionRecord.reaction_date.CopyFrom(postRecord.post_publish_date) #better post_create_date, but not available from Twitter
        postReactionRecord.reaction_like_count = postRecord.post_like_count
        postReactionRecord.reaction_content = postRecord.post_body
        postReactionRecord.user_mentions_pkey.extend([userRefPkey for userRefPkey in postRecord.user_mentions_pkey])
        return postReactionRecord
     
    def extractPlace(self,postPlace_json, postGeoaccuracy, userLanguage):
        place = postPlace_json
        placeID = place.get('id')
        if not placeID:
           log.warning(f'No PlaceGuid\n\n{postPlace_json}')
           input("Press Enter to continue... (entry will be skipped)")
           return None,postGeoaccuracy,None
        bounding_box_points = place.get('bounding_box').get('coordinates')[0]
        limYMin,limYMax,limXMin,limXMax = helperFunctions.getRectangleBounds(bounding_box_points)
        bound_points_shapely = geometry.MultiPoint([(limXMin, limYMin), (limXMax, limYMax)])
        lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
        lat_center = bound_points_shapely.centroid.coords[0][1]
        place_type = place.get('place_type')
        if place_type == "country":
            # country_guid
            # in case of country, we do not need to save the GUID from Twitter - country_code is already unique
            placeRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCountry(),place.get('country_code'),self.origin)
            if not postGeoaccuracy:
                postGeoaccuracy = lbsnPost.COUNTRY      
        elif place_type in ("city","neighborhood","admin"):
            # city_guid
            placeRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCity(),place.get('id'),self.origin)
            if not place_type == "city":
                placeRecord.sub_type = place_type
            if not postGeoaccuracy or postGeoaccuracy == lbsnPost.COUNTRY:
                postGeoaccuracy = lbsnPost.CITY
        elif place_type == "poi":
            # place_guid
            # For POIs, City is not available on Twitter
            placeRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnPlace(),place.get('id'),self.origin)
            if not postGeoaccuracy or postGeoaccuracy in (lbsnPost.COUNTRY, lbsnPost.CITY):
                postGeoaccuracy = lbsnPost.PLACE  
        else:
            log.warning(f'No Place Type Detected: {jsonStringDict}')                 
        #for some reason, twitter place entities sometimes contain linebreaks or whitespaces. We don't want this.
        placeName = place.get('name').replace('\n\r','') 
        placeName = re.sub(' +',' ',placeName) # remove multiple whitespace
        if place_type == "poi" or (userLanguage.language_short and userLanguage.language_short in ('en','und')):
            # At the moment, English name are the main references; all other language specific references are stored in name_alternatives - except for places, where twitter has no alternative place names
            # Bugfix necessary: some English names get still saved as name_alternatives
            placeRecord.name = placeName
        else:        
            placeRecord.name_alternatives.append(placeName)
        placeRecord.url = place.get('url')
        placeRecord.geom_center = "POINT(%s %s)" % (lon_center,lat_center)
        placeRecord.geom_area = Polygon(bounding_box_points).wkt # prints: 'POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))'
        refCountryRecord = None
        if not isinstance(placeRecord, lbsnCountry):
            refCountryCode = place.get('country_code')
            if refCountryCode:
                refCountryRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnCountry(),refCountryCode,self.origin)
                # At the moment, only English name references are processed
                if not userLanguage.language_short or userLanguage.language_short in ('en','und'):
                    refCountryRecord.name = place.get('country') # Needs to be saved 
                else:
                    alt_name = place.get('country')
                    refCountryRecord.name_alternatives.append(alt_name)
                self.lbsnRecords.AddRecordsToDict(refCountryRecord)
        if postGeoaccuracy == lbsnPost.CITY and refCountryRecord:
            # country_pkey only on lbsnCity(), lbsnPlace() has city_pkey, but this is not available for Twitter
            placeRecord.country_pkey.CopyFrom(refCountryRecord.pkey)
        # log.debug(f'Final Place Record: {placeRecord}')
        return placeRecord, postGeoaccuracy, refCountryRecord