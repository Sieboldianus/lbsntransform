# -*- coding: utf-8 -*-

"""
Module for mapping Flickr YFCC100M dataset to common LBSN Structure.
"""

import csv
import logging
import re
import sys
from codecs import escape_decode
from decimal import Decimal
from urllib.parse import unquote

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

# pylint: disable=no-member


class FieldMappingYFCC100M():
    """ Provides mapping function from Flickr endpoints to
        protobuf lbsnstructure
    """
    ORIGIN_NAME = "Flickr yfcc100m"
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
        self.log = logging.getLogger('__main__')  # get the main logger object
        self.skipped_count = 0
        self.skipped_low_geoaccuracy = 0
        # some records in YFCC100m are larger
        # than the default csv limit in python
        # of 131072
        csv.field_size_limit(500000)
        # self.disableReactionPostReferencing = disableReactionPostReferencing
        # self.mapFullRelations = mapFullRelations
        # self.geocodes = geocodes
        self.lic_dict = {
            "All Rights Reserved": 0,
            "Attribution-NonCommercial-ShareAlike License": 1,
            "Attribution-NonCommercial License": 2,
            "Attribution-NonCommercial-NoDerivs License": 3,
            "Attribution License": 4,
            "Attribution-ShareAlike License": 5,
            "Attribution-NoDerivs License": 6,
            "No known copyright restrictions": 7,
            "United States Government Work": 8,
            "Public Domain Dedication (CC0)": 9,
            "Public Domain Mark": 10
        }

    def parse_csv_record(self, record):
        """Entry point for flickr CSV data:
            - Decide if CSV record contains user-info or post-info
            - Skip empty or malformed records

        Attributes:
        record    A single row from CSV, stored as list type.
        """
        if len(record) == 2:
            # Flickr place record dirty detection
            lbsn_records = self.extract_flickr_place(
                record)
            return lbsn_records
        elif len(record) < 12 or not record[0].isdigit():
            # skip erroneous entries + log
            self.skipped_count += 1
            return
        else:
            # process regular Flickr yfcc100m record
            lbsn_records = self.extract_flickr_post(record)
            return lbsn_records

    def extract_flickr_post(self, record):
        """Main function for processing Flickr YFCC100M CSV entry.
           This mothod is adapted to a special structure, adapt if needed.

        To Do:
            - parameterize column numbers and structure
            - provide external config-file for specific CSV structures
            - currently not included in lbsn mapping are MachineTags,
              GeoContext (indoors, outdoors), WoeId
              and some extra attributes only present for Flickr

        Overview of available columns and examples:
        0 row-number    -   0
        1 unknown - 4e2f7a26a1dfbf165a7e30bdabf7e72a
        2 Photo/video identifier    -   6985418911
        3 User NSID     -   4e2f7a26a1dfbf165a7e30bdabf7e72a
        4 User nickname     -   39089491@N00
        5 Date taken    -   2012-02-16 09:56:37.0
        6 Date uploaded     -   1331840483
        7 Capture device    -   Canon+PowerShot+ELPH+310+HS
        8 Title     -   IMG_0520
        9 Description      -     My vacation
        10 User tags (comma-separated)   -   canon,canon+powershot+hs+310
        11 Machine tags (comma-separated)   - landscape, hills, water
        12 Longitude    -   -81.804885
        13 Latitude     -   24.550558
        14 Accuracy -   12
        15 Photo/video page URL -   http://www.flickr.com/photos/39089491@N00/6985418911/
        16 Photo/video download URL -   http://farm8.staticflickr.com/7205/6985418911_df7747990d.jpg
        17 License name -   Attribution-NonCommercial-NoDerivs License
        18 License URL  -   http://creativecommons.org/licenses/by-nc-nd/2.0/
        19 Photo/video server identifier    -   7205
        20 Photo/video farm identifier  -   8
        21 Photo/video secret   -   df7747990d
        22 Photo/video secret original  -   692d7e0a7f
        23 Extension of the original photo  -   jpg
        24 Marker (0 ¼ photo, 1 ¼ video)    -   0
        """
        # note that one input record may contain many lbsn records
        # therefore, return list of processed records
        lbsn_records = []
        # start mapping input to lbsn_records
        post_guid = record[1]
        if not HF.check_notice_empty_post_guid(post_guid):
            return None
        post_record = HF.new_lbsn_record_with_id(Post(),
                                                 post_guid,
                                                 self.origin)
        user_record = HF.new_lbsn_record_with_id(User(),
                                                 record[3],
                                                 self.origin)
        user_record.user_name = unquote(record[4]).replace(
            '+', ' ')
        user_record.url = f'http://www.flickr.com/photos/{user_record.pkey.id}/'
        if user_record:
            post_record.user_pkey.CopyFrom(user_record.pkey)
        lbsn_records.append(user_record)
        post_record.post_latlng = self.flickr_extract_postlatlng(record)
        geoaccuracy = FieldMappingYFCC100M.flickr_map_geoaccuracy(
            record[14])
        if geoaccuracy:
            post_record.post_geoaccuracy = geoaccuracy
        # place record available in separate yfcc100m dataset
        # if record[1]:
            # we need some information from postRecord to create placeRecord
            # (e.g.  user language, geoaccuracy, post_latlng)
            # some of the information from place will also modify postRecord
            # place_record = HF.new_lbsn_record_with_id(Place(),
            #                                           record[1],
            #                                           self.origin)
            # lbsn_records.append(place_record)
            # post_record.place_pkey.CopyFrom(place_record.pkey)
        post_record.post_publish_date.CopyFrom(
            HF.parse_timestamp_string_to_protobuf(record[6]))
        post_created_date = HF.parse_csv_datestring_to_protobuf(
            record[5], t_format='%Y-%m-%d %H:%M:%S.%f')
        if post_created_date:
            post_record.post_create_date.CopyFrom(
                post_created_date
            )
        post_record.post_views_count = 0
        post_record.post_comment_count = 0
        post_record.post_like_count = 0
        post_record.post_url = record[15]
        # YFCC100M dataset contains HTML codes (%20) and
        # space character is replaced by +
        post_record.post_body = unquote(record[9]).replace(
            '+', ' ')
        post_record.post_title = unquote(record[8]).replace(
            '+', ' ')
        post_record.post_thumbnail_url = record[16]  # note: fullsize url!
        # split tags by , and + because by lbsn-spec,
        # tags are limited to single word
        record_tags_list = list(
            set(filter(
                None,
                [unquote(tag)
                 for tag in re.split("[,+]+", record[10])]
            )))
        if record_tags_list:
            for tag in record_tags_list:
                tag = FieldMappingYFCC100M.clean_tags_from_flickr(tag)
                post_record.hashtags.append(tag)
        record_machine_tags = list(
            set(filter(None, [unquote(mtag) for mtag in re.split("[,+]+", record[11])])))
        if 'video' in record_machine_tags:
            # all videos appear to have 'video' in machine tags
            post_record.post_type = Post.VIDEO
        else:
            post_record.post_type = Post.IMAGE
        # replace text-string of content license by integer-id
        post_record.post_content_license = self.get_license_number_from_license_name(
            record[17])
        lbsn_records.append(post_record)
        return lbsn_records

    def extract_flickr_place(self, record):
        """Main function for processing Flickr YFCC100M Place CSV entry
        Place records are available from a separate yfcc100m dataset
        and are joined based on photo guid
        """
        # note that one input record may contain many lbsn records
        # therefore, return list of processed records
        lbsn_records = []
        # start mapping input to lbsn_records
        post_guid = record[0]
        if not record[1]:
            # skip empty records
            return None
        # place records in yfcc100m contain multiple entries, e.g.
        # 24703176:Admiralty:Suburb,24703128:Central+and+Western:Territory,24865698:Hong+Kong:Special Administrative Region,28350827:Asia%2FHong_Kong:Timezone
        place_records = record[1].split(",")
        for place_record in place_records:
            lbsn_place_record = \
                FieldMappingYFCC100M.process_place_record(
                    place_record, self.origin)
            lbsn_records.append(lbsn_place_record)
        # update post record with entries from place record
        post_record = HF.new_lbsn_record_with_id(
            Post(), post_guid, self.origin)
        for place_record in lbsn_records:
            if isinstance(place_record, Country):
                post_record.country_pkey.CopyFrom(place_record.pkey)
            if isinstance(place_record, City):
                post_record.city_pkey.CopyFrom(place_record.pkey)
            # either city or place, Twitter user cannot attach both (?)
            elif isinstance(place_record, Place):
                post_record.place_pkey.CopyFrom(place_record.pkey)
        lbsn_records.append(post_record)
        return lbsn_records

    @staticmethod
    def process_place_record(place_record, origin):
        """Assignment of Flickr place types to lbsnstructure
        hierarchy: Country, City, Place
        Original Flickr place types, which are more detailed,
        are stored in sub_type field
        """
        FLICKR_COUNTRY_MATCH = set([
            "country", "timezone", "state", "territory",
            "state/territory", "land", "arrondissement", "prefecture",
            "island", "disputed territory", "overseas collectivity",
            "overseas region", "island group"
        ])
        FLICKR_CITY_MATCH = set([
            "city", "town", "region", "special administrative region",
            "county", "district", "zip", "province", "suburb",
            "district/county", "autonomous community", "municipality",
            "department", "district/town/township", "township",
            "historical town", "governorate", "commune", "canton",
            "muhafazah", "local government area", "division", "periphery",
            "zone", "sub-region", "district/town/county", "sub-district",
            "parish", "federal district", "neighborhood", "chome", "ward",
            "sub-division", "community", "autonomous region",
            "municipal region", "emirate", "autonomous province",
            "historical county", "constituency", "entity", "colloquial",
            "circle", "quarter", "dependency", "sub-prefecture"
        ])
        FLICKR_PLACE_MATCH = set([
            "poi", "land feature", "estate", "airport", "drainage",
            "miscellaneous"
        ])
        place_record_split = place_record.split(":")
        if not len(place_record_split) == 3:
            raise ValueError(
                f'Malformed place entry:\n'
                f'place_record: {place_record}')
        place_guid = unquote(place_record_split[0])
        place_name = unquote(place_record_split[1]).replace(
            '+', ' ')
        place_type = unquote(place_record_split[2])
        place_type_lw = place_type.lower()
        place_type_lw_split = place_type_lw.split("/")
        # assignment
        if any(ptls in FLICKR_COUNTRY_MATCH for ptls in place_type_lw_split):
            lbsn_place_record = HF.new_lbsn_record_with_id(
                Country(), place_guid, origin)
        elif any(ptls in FLICKR_CITY_MATCH for ptls in place_type_lw_split):
            lbsn_place_record = HF.new_lbsn_record_with_id(
                City(), place_guid, origin)
        elif any(ptls in FLICKR_PLACE_MATCH for ptls in place_type_lw_split):
            lbsn_place_record = HF.new_lbsn_record_with_id(
                Place(), place_guid, origin)
        else:
            logging.getLogger('__main__').WARNING(
                f'Could not assign place type {place_type_lw}\n'
                f'found in place_record: {place_record}\n'
                f'Will assign default "Place"')
            lbsn_place_record = HF.new_lbsn_record_with_id(
                Place(), place_guid, origin)
        lbsn_place_record.name = place_name
        if isinstance(lbsn_place_record, City):
            # record sub types only for city and place
            lbsn_place_record.sub_type = place_type
        elif isinstance(lbsn_place_record, Place):
            lbsn_place_record.place_description = place_type
        # place_record.url (not provided)
        # need to consult post data for lat/lng coordinates
        # set to null island first
        lbsn_place_record.geom_center = "POINT(%s %s)" % (0, 0)
        return lbsn_place_record

    @staticmethod
    def clean_tags_from_flickr(tag):
        """Clean special vars not allowed in tags.
        """
        characters_to_replace = ('{', '}')
        for char_check in characters_to_replace:
            tag = tag.replace(char_check, '')
        return tag

    def get_license_number_from_license_name(self, license_name: str):
        """Flickr YFCC100M contains only full string names of licenses
        This function converts names to ids.

        Arguments:
            license_name {str} -- YFCC100M license name
        see:
        https://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html
        """
        lic_number = self.lic_dict.get(license_name)
        return lic_number

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
        lat_entry = record[13]
        lng_entry = record[12]
        if lat_entry == "" and lng_entry == "":
            l_lat, l_lng = 0, 0
        else:
            try:
                l_lng = Decimal(lng_entry)
                l_lat = Decimal(lat_entry)
            except:
                l_lat, l_lng = 0, 0

        if ((l_lat == 0 and l_lng == 0)
                or l_lat > 90 or l_lat < -90
                or l_lng > 180 or l_lng < -180):
            l_lat, l_lng = 0, 0
            self.send_to_null_island(lat_entry, lng_entry, record[5])
        return FieldMappingYFCC100M.lat_lng_to_wkt(l_lat, l_lng)

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
        # self.log.debug(f'NULL island: Guid {record_guid} - '
        #               f'Coordinates: {lat_entry}, {lng_entry}')
        self.null_island += 1
