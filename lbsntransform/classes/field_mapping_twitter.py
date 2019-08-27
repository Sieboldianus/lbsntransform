# -*- coding: utf-8 -*-

"""
Module for mapping Twitter to common LBSN Structure.
"""

# pylint: disable=no-member

import logging
import re
import sys

import shapely.geometry as geometry
# for debugging only:
from google.protobuf import text_format
from google.protobuf.timestamp_pb2 import Timestamp
from lbsnstructure.lbsnstructure_pb2 import (CompositeKey, Language,
                                             RelationshipKey, City,
                                             Country, Origin,
                                             Place, Post,
                                             PostReaction,
                                             Relationship, User,
                                             UserGroup)
from shapely.geometry.polygon import Polygon

from .helper_functions import HelperFunctions as HF
from .helper_functions import LBSNRecordDicts


class FieldMappingTwitter():
    """ Provides mapping function from Twitter endpoints to
        protobuf lbsnstructure
    """
    ORIGIN_NAME = "Twitter"
    ORIGIN_ID = 3

    def __init__(self,
                 disableReactionPostReferencing=False,
                 geocodes=False,
                 mapFullRelations=False,
                 map_reactions=True,
                 ignore_non_geotagged=False,
                 ignore_sources_set=set(),
                 min_geoaccuracy=None):
        # We're dealing with Twitter in this class,
        # lets create the OriginID globally
        # this OriginID is required for all CompositeKeys
        origin = Origin()
        origin.origin_id = Origin.TWITTER
        self.origin = origin
        # this is where all the data will be stored
        # self.lbsn_records = LBSNRecordDicts()
        self.lbsn_records = []
        self.null_island = 0
        self.log = logging.getLogger('__main__')  # logging.getLogger()
        self.disable_reaction_post_referencing = disableReactionPostReferencing
        self.map_full_relations = mapFullRelations
        self.geocodes = geocodes
        self.map_reactions = map_reactions
        self.ignore_non_geotagged = ignore_non_geotagged
        self.ignore_sources_set = ignore_sources_set
        self.min_geoaccuracy = min_geoaccuracy
        self.skipped_low_geoaccuracy = 0
        self.skipped_ignore_list = 0

    def get_skipped_geoaccuracy(self):
        """Get count of records skipped due to low geoaccuracy"""
        return self.skipped_low_geoaccuracy

    def get_skipped_ignorelist(self):
        """Get count of records skipped due to ignore list"""
        return self.skipped_ignore_list

    def parse_json_record(self, json_string_dict, input_lbsn_type=None):
        """Will parse Twitter json retrieved from Twitter API,
        returns a list of LBSN records.


        Fully extracting Twitter json's to flat relational db structure
        is challenging because Twitter json's may consist of deeply nested
        structures, which can include many LBSN record entities, e.g.:
        - the Post itself
        - the User who posted, and its attributes
        - Coordinates, Places, Cities, Countries linked to the post
        - Language of the post
        - shared or retweeted Posts and their attribues (
            Users, Places, Cities etc.)
        - mentioned users in the post ("@-mentions")
        - special jsons retrieved from other API endpoints, e.g.
            groups of users etc.

        This methods tries to do all of this automatically, but default
        values may need adjustment for specific cases. All extracted
        LBSN records are added subsequently to self.lbsn_records and
        returned finally as a single list of records in this method. This
        guarantees that db-key-relations are acknowledged when submitting
        records to db. The order of LBSN record type extraction
        follows the order of db inserts
        """
        # clear any records from previous run
        self.lbsn_records.clear()
        # decide if main object is post or user json
        if input_lbsn_type and input_lbsn_type in ('friendslist',
                                                   'followerslist'):
            for user, related_user_list in json_string_dict.items():
                user_record = HF.new_lbsn_record_with_id(
                    User(), str(user), self.origin)
                self.lbsn_records.append(user_record)
                self.extract_related_users(related_user_list,
                                           input_lbsn_type, user_record)
        elif (input_lbsn_type and input_lbsn_type == 'profile') \
                or 'screen_name' in json_string_dict:
            # user
            user_record = self.extract_user(json_string_dict)
            self.lbsn_records.append(user_record)
            # sys.exit(f'Post record: {text_format.MessageToString(userRecord,
            #                                                      as_utf8=True)}')
            if not user_record.is_private:
                # if user profile is private, we cannot access posts
                user_status = None
                if 'status' in json_string_dict:
                    user_status = json_string_dict.get('status')
                elif 'quoted_status' in json_string_dict:
                    user_status = json_string_dict.get('quoted_status')
                elif 'retweeted_status' in json_string_dict:
                    user_status = json_string_dict.get('retweeted_status')
                # in case user status is available
                if user_status:
                    self.parse_json_post(
                        user_status, userPkey=user_record.pkey)
        else:
            # otherwise, parse post
            self.parse_json_post(json_string_dict)

        # finally, return list of all extracted records
        return self.lbsn_records

    def extract_related_users(self, related_user_list,
                              input_lbsn_type, user_record):
        for related_user in related_user_list:
            related_record = HF.new_lbsn_record_with_id(User(),
                                                        str(related_user),
                                                        self.origin)
            self.lbsn_records.append(related_record)
            # note the switch of order here,
            # direction is important for 'isConnected',
            # and the different list each give us a
            # different view on this relationship
            if input_lbsn_type == 'friendslist':
                relationship_record =\
                    HF.new_lbsn_relation_with_id(Relationship(),
                                                 user_record.pkey.id,
                                                 related_record.pkey.id,
                                                 self.origin)
            elif input_lbsn_type == 'followerslist':
                relationship_record = \
                    HF.new_lbsn_relation_with_id(Relationship(),
                                                 related_record.pkey.id,
                                                 user_record.pkey.id,
                                                 self.origin)
            relationship_record.relationship_type = \
                Relationship.isCONNECTED
            self.lbsn_records.add_relationship_to_dict(
                relationship_record)

    def parse_json_post(self, json_string_dict, userPkey=None):
        """Extract json post retrieved from Twitter API

        The process is nested, but pretty linear:
        1. Extract all relevant Post Attributes
           1.a extract post coordinates
           1.b extract user attributes
           1.c extract place attributes
        (poi, city, neigborhood, admin, country)
           1.d extract extract extended tweet,
        if available, and extended entities, if available
        2. decide if post is reaction
        (reply, quote, share, see https://developer.twitter.com/
        en/docs/tweets/data-dictionary/overview/entities-object.html)
        3. if post is reaction, copy reduced reaction
        attributes from extracted Post
        4. add post/reaction to recordDict
        5. process all referenced posts
           5.a Retweet(=Share) and Quote Tweets are special kinds
        of Tweets that contain the original Tweet as an embedded object.
           5.b Retweets have a top-level "retweeted_status"
        object, and Quoted Tweets have a "quoted_status" object
        process tweet-post object

        Note: one input record may contain many lbsn records
        therefore, records are first added to self.lbsn_records
        to be later returned together
        """
        post_record = self.extract_post(
            json_string_dict, userPkey)

        if not post_record:
            # in case no post record has been extracted
            # (e.g. non_geotagged clause)
            return
        # Assignment Step
        # check if post is reaction to other post
        # reaction means: reduced structure compared to post;
        # reactions often include the complete original post,
        # therefore nested processing necessary
        if HF.is_post_reaction(json_string_dict):
            if self.map_reactions is False:
                return
            post_reaction_record = self.map_postrecord_to_postreactionrecord(
                post_record)
            refuser_pkey = None
            if 'quoted_status' in json_string_dict:
                # Note: Quote is both: Share & Reply
                if 'user' not in json_string_dict.get('quoted_status'):
                    refuser_pkey = \
                        HF.substitute_referenced_user(json_string_dict,
                                                      self.origin,
                                                      self.log)
                post_reaction_record.reaction_type = PostReaction.QUOTE
                ref_post_record = self.extract_post(
                    json_string_dict.get('quoted_status'))
            elif 'retweeted_status' in json_string_dict:
                # Note: No retweets are available when data is queried
                # using Bounding Box because of Geo-Tweet limitation:
                # "Note that native Retweets are not matched by this
                # parameter. While the original Tweet may have a location,
                # the Retweet will not"
                # see https://developer.twitter.com/en/docs/
                # tweets/filter-realtime/guides/basic-stream-parameters.html
                if 'user' not in json_string_dict.get('retweeted_status'):
                    # Current issue with Twitter search: the retweeting
                    # user is not returned in retweeted_status
                    # but we can get this from other information,
                    # such as user_mentions field from the retweet
                    # https://twittercommunity.com/t/status-retweeted-
                    # status-quoted-status-user-missing-from-search-tweets-json-response/63355
                    refuser_pkey = \
                        HF.substitute_referenced_user(json_string_dict,
                                                      self.origin,
                                                      self.log)
                post_reaction_record.reaction_type = PostReaction.SHARE
                retweet_post = json_string_dict.get('retweeted_status')
                ref_post_record = self.extract_post(retweet_post, refuser_pkey)

            elif json_string_dict.get('in_reply_to_status_id_str'):
                # if reply, original tweet is not available (?)
                post_reaction_record.reaction_type = PostReaction.COMMENT
                ref_post_record = \
                    HF.new_lbsn_record_with_id(Post(),
                                               json_string_dict.get(
                        'in_reply_to_status_id_str'),
                        self.origin)
                ref_user_record = \
                    HF.new_lbsn_record_with_id(User(),
                                               json_string_dict.get(
                        'in_reply_to_user_id_str'),
                        self.origin)
                ref_user_record.user_name = json_string_dict.get(
                    'in_reply_to_screen_name')  # Needs to be saved
                self.lbsn_records.append(ref_user_record)
                ref_post_record.user_pkey.CopyFrom(ref_user_record.pkey)

            # add referenced post pkey to reaction
            if not self.disable_reaction_post_referencing:
                post_reaction_record.referencedPost_pkey.CopyFrom(
                    ref_post_record.pkey)
                # ToDo: if a Reaction refers to another
                # reaction (Information Spread)
                # This information is currently not
                # [available from Twitter](https://developer.twitter.com/
                # en/docs/tweets/data-dictionary/overview/tweet-object):
                # "Note that retweets of retweets do not show
                # representations of the intermediary retweet [...]"
                # would be added to
                # postReactionRecord.referencedPostReaction_pkey
                if ref_post_record:
                    self.lbsn_records.append(ref_post_record)
            # add postReactionRecord to Dict
            self.lbsn_records.append(post_reaction_record)
        else:
            # otherwise add post to self.lbsn_records
            # which already includes all other entries (User, City, Place etc.)
            self.lbsn_records.append(post_record)

    def extract_user(self, json_string_dict):
        user = json_string_dict
        user_record = HF.new_lbsn_record_with_id(User(),
                                                 user.get(
                                                 'id_str'),
                                                 self.origin)
        # get additional information about the user, if available
        user_record.user_fullname = user.get('name')
        user_record.follows = user.get('friends_count')
        user_record.is_private = user.get('protected')
        user_record.followed = user.get('followers_count')
        user_bio = user.get('description')
        if user_bio:
            user_record.biography = user_bio
        user_record.user_name = user.get('screen_name')
        listed_count = user.get('listed_count')
        if listed_count:
            user_record.group_count = listed_count
        user_record.post_count = user.get('statuses_count')
        user_record.url = f'https://twitter.com/intent/user?user_id=' \
                          f'{user_record.pkey.id}'
        ref_user_language = Language()
        ref_user_language.language_short = user.get('lang')
        user_record.user_language.CopyFrom(ref_user_language)
        user_location = user.get('location')
        if user_location:
            user_record.user_location = user_location
            if self.geocodes and user_record.user_location in self.geocodes:
                l_lat = self.geocodes[user_record.user_location][0]
                l_lng = self.geocodes[user_record.user_location][1]
                user_record.user_location_geom = "POINT(%s %s)" % (
                    l_lng, l_lat)
        # userGeoLocation = user.get('profile_location') # todo!
        user_record.liked_count = user.get('favourites_count')
        user_record.active_since.CopyFrom(
            HF.json_date_string_to_proto(user.get('created_at')))
        user_profile_image_url = user.get('profile_image_url')
        if not user_profile_image_url == f'http://abs.twimg.com/sticky/' \
                                         f'default_profile_images/' \
                                         f'default_profile_normal.png':
            user_record.profile_image_url = user_profile_image_url
        user_timezone = user.get('time_zone')
        if user_timezone:
            user_record.user_timezone = user_timezone
        user_utc_offset = user.get('utc_offset')
        if user_utc_offset:
            user_record.user_utc_offset = user_utc_offset
        # the following example demonstrates specific information
        # that cannot be extracted from twitter post data
        # deutscherBundestagGroup = \
        # HF.createNewLBSNRecord_with_id(UserGroup(),
        #                               "MdB (Bundestag)",
        #                               self.origin)
        # userRecord.user_groups_member.append(
        #    deutscherBundestagGroup.pkey.id)
        # if self.mapFullRelations:
        #       relationshipRecord = \
        #       HF.createNewLBSNRelationship_with_id(Relationship(),
        #                                            userRecord.pkey.id,
        #                                            deutscherBundestagGroup.pkey.id,
        #                                            self.origin)
        #       relationshipRecord.relationship_type = Relationship.inGROUP
        #       self.lbsn_records.AddRelationshipToDict(relationshipRecord)
        # userRecord.user_groups_follows = []
        return user_record

    def extract_post(self, json_string_dict, user_pkey=None):
        """Returns tuple of Post() and List of post_context_records

        e.g.:
            (Post(), [Country(), City(), Place(), User()])
        """
        post_guid = json_string_dict.get('id_str')

        if not HF.check_notice_empty_post_guid(post_guid):
            return None, None
        post_record = HF.new_lbsn_record_with_id(Post(),
                                                 post_guid,
                                                 self.origin)
        post_geoacc = None
        user_record = None
        user_info = json_string_dict.get('user')
        if user_info:
            # Get Post/Reaction Details of User
            user_record = self.extract_user(json_string_dict.get('user'))
        elif user_pkey:
            # userPkey is already available for posts that are statuses
            user_record = HF.new_lbsn_record_with_id(User(),
                                                     user_pkey.id,
                                                     self.origin)
        if user_record:
            # self.lbsn_records.append(user_record)
            self.lbsn_records.append(user_record)
        else:
            self.log.warning(f'Record {self.lbsn_records.count_glob_total}: '
                             f'No User record found for post: {post_guid} '
                             f'(post saved without userid)..')
            print(f'Record {self.lbsn_records.count_glob_total}', end='\r')

        # Some preprocessing for all types:
        post_coordinates = json_string_dict.get('coordinates')
        if post_coordinates:
            l_lng = post_coordinates.get('coordinates')[0]
            l_lat = post_coordinates.get('coordinates')[1]
            post_record.post_geoaccuracy = Post.LATLNG
            post_record.post_latlng = "POINT(%s %s)" % (l_lng, l_lat)

        # Check if Place is mentioned
        post_place_json = json_string_dict.get('place')
        if post_place_json:
            # we need some information from postRecord to create placeRecord
            # (e.g. user language, geoaccuracy, post_latlng)
            # some of the information from place will also modify postRecord
            # attributes; therefore return both
            if user_record:
                user_lang = user_record.user_language
            else:
                user_lang = None
            place_record, \
                post_geoacc, \
                post_country = self.extract_place(post_place_json,
                                                  post_record.post_geoaccuracy,
                                                  user_lang)
            if not post_record.post_geoaccuracy:
                post_record.post_geoaccuracy = post_geoacc
            # postRecord.post_geoaccuracy = twitterPostAttributes.geoaccuracy
            # self.lbsn_records.append(place_record)
            self.lbsn_records.append(place_record)
            if post_country:
                post_record.country_pkey.CopyFrom(post_country.pkey)
            if isinstance(place_record, City):
                post_record.city_pkey.CopyFrom(place_record.pkey)
            # either city or place, Twitter user cannot attach both (?)
            elif isinstance(place_record, Place):
                post_record.place_pkey.CopyFrom(place_record.pkey)
            # substitute postRecord LatLng Coordinates from placeRecord,
            # if not already set
            if not post_record.post_latlng:
                # Note: this will also substitute Country lat/lng in post
                # this information is also available by query of
                # country_guid in posts
                # use input arg min_geoaccuracy to exclude country geo-posts
                post_record.post_latlng = place_record.geom_center
        # if still no geoinformation, send post to Null-Island
        if not post_record.post_latlng:
            if self.ignore_non_geotagged is True:
                return None
            else:
                # print(
                #     f'post_geoacc: ' \
                #     f'{Post.PostGeoaccuracy.Name(post_geoacc)}')
                # sys.exit(f'{json_string_dict}')
                self.null_island += 1
                post_record.post_latlng = "POINT(%s %s)" % (0, 0)
        if self.min_geoaccuracy:
            if not HF.geoacc_within_threshold(post_record.post_geoaccuracy,
                                              self.min_geoaccuracy):
                self.skipped_low_geoaccuracy += 1
                return None
        # Process attributes of twitter post
        post_source = json_string_dict.get('source')
        if post_source:
            post_record.input_source = HF.cleanhtml(
                json_string_dict.get('source'))
            if self.ignore_sources_set and \
                    post_record.input_source in self.ignore_sources_set:
                # skip entry if in ignore list
                self.skipped_ignore_list += 1
                return None
        post_record.post_publish_date.CopyFrom(
            HF.json_date_string_to_proto(json_string_dict.get('created_at')))
        if user_record:
            post_record.user_pkey.CopyFrom(user_record.pkey)

        def value_count(x): return 0 if x is None else x
        post_record.post_quote_count = value_count(
            json_string_dict.get('quote_count'))
        post_record.post_comment_count = value_count(
            json_string_dict.get('reply_count'))
        post_record.post_share_count = value_count(
            json_string_dict.get('retweet_count'))
        post_record.post_like_count = value_count(
            json_string_dict.get('favorite_count'))
        post_record.post_url = f'https://twitter.com/statuses/{post_guid}'
        language_str = json_string_dict.get('lang')
        if language_str:
            post_language = Language()
            post_language.language_short = json_string_dict.get('lang')
            post_record.post_language.CopyFrom(post_language)
        # If Extended_tweet object is available,
        # process entities and post_body (text) data from extended object
        is_truncated = json_string_dict.get('truncated')
        if is_truncated and 'extended_tweet' in json_string_dict:
            # if the "truncated" field is set to true,
            # and the "extended_tweet" object provides complete
            # "full_text" and "entities" Tweet metadata
            # Source for all data is extended object, if available
            json_string_dict = json_string_dict.get('extended_tweet')
            post_record.post_body = json_string_dict.get('full_text')
            # else:
            #    self.log.warning(f'Truncated but no extended_tweet:'
            #                     f'{json_string_dict}')
            #    input("Press Enter to continue... (entry will be skipped)")
            #    return None
        else:
            if 'full_text' in json_string_dict:
                post_record.post_body = json_string_dict.get('full_text')
            else:
                post_record.post_body = json_string_dict.get('text')
        # entities section always exists and includes meta information
        # such as hashtags or user_mentions
        entities_json = json_string_dict.get('entities')
        # extract hashtags
        hashtags_json = entities_json.get('hashtags')
        if hashtags_json:
            for hashtag in hashtags_json:  # iterate over the list
                post_record.hashtags.append(hashtag.get("text"))
        # Look for mentioned userRecords
        user_mentions_json = entities_json.get('user_mentions')
        if user_mentions_json:
            ref_user_records = HF.get_mentioned_users(user_mentions_json,
                                                      self.origin)
            # self.lbsn_records.append(ref_user_records)
            self.lbsn_records.append(ref_user_records)
            post_record.user_mentions_pkey.extend(
                [user_ref.pkey for user_ref in ref_user_records])
            if self.map_full_relations:
                self.extract_mentioned_users(
                    ref_user_records, user_record.pkey.id)
        # sometimes, extended_entities section exists and includes
        # additional information on media, but never hashtags or user_mentions
        # Since the media type metadata in the extended_entities section
        # correctly indicates the media type
        # (‘photo’, ‘video’ or ‘animated_gif’),
        # and supports up to 4 photos, it is the preferred metadata
        # source for native media. See:
        # https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/extended-entities-object.html#extended-entities-object
        if 'extended_entities' in json_string_dict:
            entities_json = json_string_dict.get('extended_entities')
        media_json = entities_json.get('media')
        if media_json:
            post_record.post_type = HF.assign_media_post_type(media_json)
        else:
            post_record.post_type = Post.TEXT
        post_record.emoji.extend(HF.extract_emoji(post_record.post_body))
        # because standard print statement will produce escaped text,
        # we can use protobuf text_format to give us a human friendly
        # version of the text
        # log.debug(f'Post record: '
        #           f'{text_format.MessageToString(postRecord, as_utf8=True)}')
        # log.debug(f'Post record: {postRecord}')
        return post_record

    def extract_mentioned_users(self, ref_user_records, user_record_id):
        for mentioned_user_record in ref_user_records:
            relation_record = \
                HF.new_lbsn_relation_with_id(Relationship(),
                                             user_record_id,
                                             mentioned_user_record.pkey.id,
                                             self.origin)
            relation_record.relationship_type = \
                Relationship.MENTIONS_USER
            self.lbsn_records.add_relationship_to_dict(
                relation_record)

    def map_postrecord_to_postreactionrecord(self, post_record):
        post_reaction_record = PostReaction()
        post_reaction_record.pkey.CopyFrom(post_record.pkey)
        post_reaction_record.user_pkey.CopyFrom(post_record.user_pkey)
        post_reaction_record.reaction_latlng = post_record.post_latlng
        # better post_create_date, but not available from Twitter
        post_reaction_record.reaction_date.CopyFrom(
            post_record.post_publish_date)
        post_reaction_record.reaction_like_count = post_record.post_like_count
        post_reaction_record.reaction_content = post_record.post_body
        post_reaction_record.user_mentions_pkey.extend(
            [userRefPkey for userRefPkey in post_record.user_mentions_pkey])
        return post_reaction_record

    def extract_place(self, postplace_json,
                      post_geoaccuracy, user_language=None):
        place = postplace_json
        place_id = place.get('id')
        if not place_id:
            self.log.warning(f'No PlaceGuid\n\n{place}')
            input("Press Enter to continue... (entry will be skipped)")
            return None, post_geoaccuracy, None
        lon_center = 0
        lat_center = 0
        bounding_box = place.get('bounding_box')
        if bounding_box:
            bound_coordinates = bounding_box.get('coordinates')
            if bound_coordinates:
                bounding_box_points = bound_coordinates[0]
            lim_y_min, lim_y_max, lim_x_min, lim_x_max = \
                HF.get_rectangle_bounds(bounding_box_points)
            bound_points_shapely = \
                geometry.MultiPoint([(lim_x_min, lim_y_min),
                                     (lim_x_max, lim_y_max)])
            # True centroid (coords may be multipoint)
            lon_center = bound_points_shapely.centroid.coords[0][0]
            lat_center = bound_points_shapely.centroid.coords[0][1]
        place_type = place.get('place_type')
        if place_type == "country":
            # country_guid
            # in case of country,
            # we do not need to save the GUID from Twitter
            # - country_code is already unique
            country_code = place.get('country_code')
            if country_code:
                place_record = HF.new_lbsn_record_with_id(Country(),
                                                          place.get(
                    'country_code'),
                    self.origin)
                if not post_geoaccuracy:
                    post_geoaccuracy = Post.COUNTRY
            else:
                self.log.warning(
                    f'No country_code\n\n{place}. '
                    f'PlaceEntry will be skipped..')
                return None, post_geoaccuracy, None
        elif place_type in ("city", "neighborhood", "admin"):
            # city_guid
            place_record = HF.new_lbsn_record_with_id(City(),
                                                      place.get(
                'id'),
                self.origin)
            if not place_type == "city":
                place_record.sub_type = place_type
            if not post_geoaccuracy or post_geoaccuracy == Post.COUNTRY:
                post_geoaccuracy = Post.CITY
        elif place_type == "poi":
            # place_guid
            # For POIs, City is not available on Twitter
            place_record = HF.new_lbsn_record_with_id(Place(),
                                                      place.get(
                'id'),
                self.origin)
            if not post_geoaccuracy or post_geoaccuracy in (Post.COUNTRY,
                                                            Post.CITY):
                post_geoaccuracy = Post.PLACE
        else:
            self.log.warning(f'No Place Type Detected: {place}')
        # for some reason, twitter place entities sometimes contain
        # linebreaks or whitespaces. We don't want this.
        place_name = place.get('name').replace('\n\r', '')
        # remove multiple whitespace
        place_name = re.sub(' +', ' ', place_name)
        if place_type == "poi" or \
           user_language is None \
           or not user_language.language_short \
           or user_language.language_short in ('en', 'und'):
            # At the moment, English name are the main references;
            # all other language specific references are stored in
            # name_alternatives - except for places, where twitter
            # has no alternative place names
            # Bugfix necessary: some English names get still saved
            # as name_alternatives
            place_record.name = place_name
        else:
            place_record.name_alternatives.append(place_name)
        place_record.url = place.get('url')
        place_record.geom_center = "POINT(%s %s)" % (lon_center, lat_center)
        if bounding_box and bound_coordinates:
            # prints: 'POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))'
            place_record.geom_area = Polygon(bounding_box_points).wkt
        ref_country_record = None
        if not isinstance(place_record, Country):
            ref_country_code = place.get('country_code')
            if ref_country_code:
                ref_country_record = \
                    HF.new_lbsn_record_with_id(Country(),
                                               ref_country_code,
                                               self.origin)
                # At the moment, only English name references are processed
                if user_language is None \
                   or not user_language.language_short \
                   or user_language.language_short in ('en', 'und'):
                    ref_country_record.name = place.get(
                        'country')  # Needs to be saved
                else:
                    alt_name = place.get('country')
                    ref_country_record.name_alternatives.append(alt_name)
                self.lbsn_records.append(ref_country_record)
        if post_geoaccuracy == Post.CITY and ref_country_record:
            # country_pkey only on City(), Place() has city_pkey,
            # but this is not available for Twitter
            place_record.country_pkey.CopyFrom(ref_country_record.pkey)
        # log.debug(f'Final Place Record: {placeRecord}')
        return place_record, post_geoaccuracy, ref_country_record
