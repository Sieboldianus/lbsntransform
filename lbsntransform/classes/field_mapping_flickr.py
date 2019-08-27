# -*- coding: utf-8 -*-

"""
Module for mapping Flickr to common LBSN Structure.
"""

# pylint: disable=no-member

import logging
from decimal import Decimal

# for debugging only:
from google.protobuf import text_format
from lbsnstructure.lbsnstructure_pb2 import (CompositeKey, Language,
                                             RelationshipKey, City,
                                             Country, Origin,
                                             Place, Post,
                                             PostReaction,
                                             Relationship, User,
                                             UserGroup)

from .helper_functions import HelperFunctions as HF
from .helper_functions import LBSNRecordDicts


class FieldMappingFlickr():
    """ Provides mapping function from Flickr endpoints to
        protobuf lbsnstructure
    """
    ORIGIN_NAME = "Flickr"
    ORIGIN_ID = 2

    def __init__(self,
                 disable_reaction_post_referencing=False,
                 geocodes=False,
                 map_full_relations=False,
                 map_reactions=True,
                 ignore_non_geotagged=False,
                 ignore_sources_set=set(),
                 min_geoaccuracy=None):
        # We're dealing with Flickr in this class, lets create the OriginID
        # globally
        # this OriginID is required for all CompositeKeys
        origin = Origin()
        origin.origin_id = Origin.FLICKR
        self.origin = origin
        self.null_island = 0
        # this is where all the data will be stored
        self.lbsn_records = []
        self.log = logging.getLogger('__main__')  # get the main logger object
        self.skipped_count = 0
        self.skipped_low_geoaccuracy = 0
        # self.disableReactionPostReferencing = disableReactionPostReferencing
        # self.mapFullRelations = mapFullRelations
        # self.geocodes = geocodes

    def parse_csv_record(self, record):
        """Entry point for flickr CSV data:
            - Decide if CSV record contains user-info or post-info
            - Skip empty or malformed records

        Attributes:
        record    A single row from CSV, stored as list type.
        """
        self.lbsn_records.clear()
        if len(record) < 12 or not record[0].isdigit():
            # skip
            self.skipped_count += 1
            return
        else:
            self.extract_flickr_post(record)
        return self.lbsn_records

    def extract_flickr_post(self, record):
        """Main function for processing Flickr CSV entry.
           This mothod is adapted to a special structure, adapt if needed.

        To Do:
            - parameterize column numbers and structure
            - provide external config-file for specific CSV structures
            - currently not included in lbsn mapping are MachineTags,
              GeoContext (indoors, outdoors), WoeId
              and some extra attributes only present for Flickr
        """
        post_guid = record[5]
        if not HF.check_notice_empty_post_guid(post_guid):
            return None
        post_record = HF.new_lbsn_record_with_id(Post(),
                                                 post_guid,
                                                 self.origin)
        user_record = HF.new_lbsn_record_with_id(User(),
                                                 record[7],
                                                 self.origin)
        user_record.user_name = record[6]
        user_record.url = f'http://www.flickr.com/photos/{user_record.pkey.id}/'
        if user_record:
            post_record.user_pkey.CopyFrom(user_record.pkey)
        self.lbsn_records.append(user_record)
        post_record.post_latlng = self.flickr_extract_postlatlng(record)
        geoaccuracy = FieldMappingFlickr.flickr_map_geoaccuracy(record[13])
        if geoaccuracy:
            post_record.post_geoaccuracy = geoaccuracy
        if record[19]:
            # we need some information from postRecord to create placeRecord
            # (e.g.  user language, geoaccuracy, post_latlng)
            # some of the information from place will also modify postRecord
            place_record = HF.new_lbsn_record_with_id(Place(),
                                                      record[19],
                                                      self.origin)
            self.lbsn_records.append(place_record)
            post_record.place_pkey.CopyFrom(place_record.pkey)
        post_record.post_publish_date.CopyFrom(
            HF.parse_csv_datestring_to_protobuf(record[9]))
        post_record.post_create_date.CopyFrom(
            HF.parse_csv_datestring_to_protobuf(record[8]))
        # valueCount = lambda x: 0 if x is None else x

        def value_count(x): return int(x) if x.isdigit() else 0
        post_record.post_views_count = value_count(record[10])
        post_record.post_comment_count = value_count(record[18])
        post_record.post_like_count = value_count(record[17])
        post_record.post_url = f'http://flickr.com/photo.gne?id={post_guid}'
        post_record.post_body = FieldMappingFlickr.reverse_csv_comma_replace(
            record[21])
        post_record.post_title = FieldMappingFlickr.reverse_csv_comma_replace(
            record[3])
        post_record.post_thumbnail_url = record[4]
        record_tags_list = list(filter(None, record[11].split(";")))
        if record_tags_list:
            for tag in record_tags_list:
                tag = FieldMappingFlickr.clean_tags_from_flickr(tag)
                post_record.hashtags.append(tag)
        record_media_type = record[16]
        if record_media_type and record_media_type == "video":
            post_record.post_type = Post.VIDEO
        else:
            post_record.post_type = Post.IMAGE
        post_record.post_content_license = value_count(record[14])
        self.lbsn_records.append(post_record)

    @staticmethod
    def reverse_csv_comma_replace(csv_string):
        """Flickr CSV data is stored without quotes by replacing commas with semicolon.
        This functon will reverse replacement.
        """
        return csv_string.replace(";", ",")

    @staticmethod
    def clean_tags_from_flickr(tag):
        """Clean special vars not allowed in tags.
        """
        characters_to_replace = ('{', '}')
        for char_check in characters_to_replace:
            tag = tag.replace(char_check, '')
        return tag

    @staticmethod
    def flickr_map_geoaccuracy(flickr_geo_accuracy_level):
        """Flickr Geoaccuracy Levels (16) are mapped to four LBSNstructure levels:
           LBSN PostGeoaccuracy: UNKNOWN = 0; LATLNG = 1; PLACE = 2; CITY = 3;
           COUNTRY = 4
           Fickr: World level is 1, Country is ~3, Region ~6, City ~11,
           Street ~16.

           Flickr Current range is 1-16. Defaults to 16 if not specified.

        Attributes:
        flickr_geo_accuracy_level   Geoaccuracy Level returned from Flickr
        (String, e.g.: "Level12")
        """
        lbsn_geoaccuracy = False
        stripped_level = flickr_geo_accuracy_level.lstrip('Level').strip()
        if stripped_level.isdigit():
            stripped_level = int(stripped_level)
            if stripped_level >= 15:
                lbsn_geoaccuracy = Post.LATLNG
            elif stripped_level >= 12:
                lbsn_geoaccuracy = Post.PLACE
            elif stripped_level >= 8:
                lbsn_geoaccuracy = Post.CITY
            else:
                lbsn_geoaccuracy = Post.COUNTRY
        else:
            if flickr_geo_accuracy_level == "Street":
                lbsn_geoaccuracy = Post.LATLNG
            elif flickr_geo_accuracy_level in ("City", "Region"):
                lbsn_geoaccuracy = Post.CITY
            elif flickr_geo_accuracy_level in ("Country", "World"):
                lbsn_geoaccuracy = Post.COUNTRY
        return lbsn_geoaccuracy

    def flickr_extract_postlatlng(self, record):
        """Basic routine for extracting lat/lng coordinates from post.
           - checks for consistency and errors
           - in case of any issue, entry is submitted to Null island (0, 0)
        """
        lat_entry = record[1]
        lng_entry = record[2]
        if lat_entry == "" and lng_entry == "":
            l_lat, l_lng = 0, 0
        else:
            try:
                l_lng = Decimal(lng_entry)
                l_lat = Decimal(lat_entry)
            except:
                l_lat, l_lng = 0, 0

        if (l_lat == 0 and l_lng == 0) \
                or l_lat > 90 or l_lat < -90 \
                or l_lng > 180 or l_lng < -180:
            l_lat, l_lng = 0, 0
            self.send_to_null_island(lat_entry, lng_entry, record[5])
        return FieldMappingFlickr.lat_lng_to_wkt(l_lat, l_lng)

    @staticmethod
    def lat_lng_to_wkt(lat, lng):
        """Convert lat lng to WKT (Well-Known-Text)
        """
        point_latlng_string = "POINT(%s %s)" % (lng, lat)
        return point_latlng_string

    def send_to_null_island(self, lat_entry, lng_entry, record_guid):
        """Logs entries with problematic lat/lng's,
           increases Null Island Counter by 1.
        """
        self.log.debug(f'NULL island: Guid {record_guid} - '
                       f'Coordinates: {lat_entry}, {lng_entry}')
        self.null_island += 1
