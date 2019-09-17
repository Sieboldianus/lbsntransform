# -*- coding: utf-8 -*-

"""
Module for mapping public Facebook Place Graph to common LBSN Structure.
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


class FieldMappingFB():
    """ Provides mapping function from Facebook Place Graph endpoints to
        protobuf lbsnstructure
    """
    ORIGIN_NAME = "Facebook"
    ORIGIN_ID = 4

    def __init__(self,
                 disableReactionPostReferencing=False,
                 geocodes=False,
                 mapFullRelations=False,
                 map_reactions=True,
                 ignore_non_geotagged=False,
                 ignore_sources_set=set(),
                 min_geoaccuracy=None):
        origin = Origin()
        origin.origin_id = Origin.TWITTER
        self.origin = origin
        # this is where all the data will be stored
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
        """Will parse Facebook json retrieved from Facebook Places Graph,
        returns a list of LBSN records.
        """
        # clear any records from previous run
        self.lbsn_records.clear()
        # decide if main object is place
        if input_lbsn_type and input_lbsn_type in ('placepage'):
            # place
            place_record = self.extract_place(json_string_dict)
            self.lbsn_records.append(place_record)
        else:
            # otherwise, raise error
            raise ValueError("Input type not supported")
        # finally, return list of all extracted records
        return self.lbsn_records

    def extract_place(self, postplace_json):
        place = postplace_json
        place_id = place.get('id')

        if not place_id:
            self.log.warning(f'No PlaceGuid\n\n{place}')
            input("Press Enter to continue... (entry will be skipped)")
            return None
        lon_center = 0
        lat_center = 0
        place_center = place.get('location')
        if place_center:
            # centroid
            lon_center = place_center.get('longitude')
            lat_center = place_center.get('latitude')
        place_cat_list = place.get('category_list')
        if place_cat_list:
            first_cat = place_cat_list[0]
            first_cat_name = first_cat.get("name")
            if first_cat_name == "country":
                place_record = HF.new_lbsn_record_with_id(
                    Country(), place_id, self.origin)
            elif first_cat_name in ("city", "neighborhood", "admin"):
                place_record = HF.new_lbsn_record_with_id(
                    City(), place_id, self.origin)
            else:
                # all other cat types
                place_record = HF.new_lbsn_record_with_id(
                    Place(), place_id, self.origin)
        if isinstance(place_record, Place):
            # place specific
            input(type(place_cat_list))
            if place_cat_list:
                place_record.attributes = place_cat_list
            place_opening_hours = place.get('hours')
            if place_opening_hours:
                # merge dictionaries (shallow)
                place_record.attributes = {
                    **place_record.attributes, **place_opening_hours}
            rating_count = place.get('rating_count')
            if rating_count:
                # merge dictionaries (shallow)
                place_record.attributes["rating_count"] = rating_count
            about = place.get('about')
            if about:
                # merge dictionaries (shallow)
                place_record.attributes["about"] = about
            place_record.like_count = place.get('engagement').get('count')
            place_record.checkin_count = place.get('checkins')
            place_record.place_description = place.get('description')
            place_record.zip_code = place.get('zip')
            place_record.address = FieldMappingFB.compile_address(place)
            place_record.place_phone = place.get('description')
        # same for Country, City and Place
        place_name = place.get('name').replace('\n\r', '')
        # remove multiple whitespace
        place_name = re.sub(' +', ' ', place_name)
        place_record.name = place_name
        place_record.url = place.get('link')
        place_record.geom_center = "POINT(%s %s)" % (lon_center, lat_center)
        # return
        return place_record


@staticmethod
def compile_address(fb_place_dict):
    single_line_address = fb_place_dict.get("single_line_address")
    if single_line_address:
        return single_line_address
    else:
        fb_city = fb_place_dict.get("city")
        fb_country = fb_place_dict.get("country")
        fb_street = fb_place_dict.get("street")
        fb_address = ', '.join([fb_street, fb_city, fb_country])
        return fb_address
