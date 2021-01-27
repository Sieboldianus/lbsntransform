# -*- coding: utf-8 -*-

"""
Module for mapping LBSN (RAW) to common LBSN Structure (Protobuf).
"""

# pylint: disable=no-member

import logging
from typing import Optional, Dict, Any
from lbsnstructure import lbsnstructure_pb2 as lbsn
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.duration_pb2 import Duration
from shapely import wkb

from lbsntransform.tools.helper_functions import HelperFunctions as HF

MAPPING_ID = 0

def parse_geom(geom_hex):
    """Parse Postgis hex WKB to geometry WKT"""
    geom = wkb.loads(geom_hex, hex=True)
    return geom.wkt


def set_lbsn_attr(lbsn_obj, attr_name, in_record, geom: Optional[bool] = None):
    """Sets value for attr_name of lbsn_obj if
    attr_value is not None"""
    attr_value = in_record.get(attr_name)
    if attr_value is None:
        return
    if isinstance(attr_value, (list, dict)):
        if len(attr_value) == 0:
            return
        getattr(lbsn_obj, attr_name).extend(attr_value)
        return
    if geom:
        attr_value = parse_geom(attr_value)
    setattr(lbsn_obj, attr_name, attr_value)


def copydate_lbsn_attr(lbsn_obj_attr, copy_from_val):
    """Some protobuf fields cannot be assigned directly,
    this function applies copyfrom assignment"""
    date_pb = Timestamp()
    date_pb.FromDatetime(
        copy_from_val)
    lbsn_obj_attr.CopyFrom(
        date_pb)

def copyduration_lbsn_attr(lbsn_obj_attr, copy_from_val):
    """Some protobuf fields cannot be assigned directly,
    this function applies copyfrom assignment"""
    duration_pb = Duration()
    duration_pb.FromString(
        copy_from_val)
    lbsn_obj_attr.CopyFrom(
        duration_pb)

def set_lbsn_pkey(lbsn_obj_pkey, pkey_obj, pkey_val, origin_val):
    """Sets value for lbsn_obj_pkey of pkey_obj if
    pkey_val is not None"""
    if pkey_val is None:
        return
    pkey_obj = HF.new_lbsn_record_with_id(
        pkey_obj, pkey_val, origin_val)
    lbsn_obj_pkey.CopyFrom(
        pkey_obj.pkey)


class importer():
    """ Provides mapping function from LBSN (raw) endpoints to
        protobuf lbsnstructure
    """
    ORIGIN_NAME = "LBSN"
    ORIGIN_ID = 0

    def __init__(self,
                 disable_reaction_post_referencing=False,
                 geocodes=False,
                 map_full_relations=False,
                 map_reactions=True,
                 ignore_non_geotagged=False,
                 ignore_sources_set=None,
                 min_geoaccuracy=None):
        # We're dealing with LBSN in this class, lets create the OriginID
        # globally
        # this OriginID is required for all CompositeKeys
        origin = lbsn.Origin()
        origin.origin_id = lbsn.Origin.LBSN
        self.origin = origin
        self.null_island = 0
        # this is where all the data will be stored
        # self.lbsn_records = []
        self.log = logging.getLogger('__main__')  # get the main logger object
        self.skipped_count = 0
        self.skipped_low_geoaccuracy = 0
        # self.disableReactionPostReferencing = disableReactionPostReferencing
        # self.mapFullRelations = mapFullRelations
        # self.geocodes = geocodes

    @classmethod
    def get_func_record(cls, record: Dict[str, Any], input_type: Optional[str] = None):
        """Returns mapping function for input_type"""
        FUNC_MAP = {
            lbsn.Origin().DESCRIPTOR.name: cls.extract_origin,
            lbsn.Country().DESCRIPTOR.name: cls.extract_country,
            lbsn.City().DESCRIPTOR.name: cls.extract_city,
            lbsn.Place().DESCRIPTOR.name: cls.extract_place,
            lbsn.UserGroup().DESCRIPTOR.name: cls.extract_usergroup,
            lbsn.User().DESCRIPTOR.name: cls.extract_user,
            lbsn.Post().DESCRIPTOR.name: cls.extract_post,
            lbsn.PostReaction().DESCRIPTOR.name: cls.extract_postreaction,
            lbsn.Event().DESCRIPTOR.name: cls.extract_event,
        }
        func_map = FUNC_MAP.get(input_type)
        # create origin always the same
        origin = lbsn.Origin()
        origin.origin_id = record.get('origin_id')
        return func_map(record, origin)

    def parse_json_record(
            self, record: Dict[str, Any], input_type: Optional[str] = None):
        """Entry point for LBSN data:

        Attributes:
        record: tuple
            0:    A single row from LBSN, stored as dict
            1:    input_type    Type of LBSN record (User, Post, Place etc.)
        """
        record = self.get_func_record(record, input_type)
        # return list of single item
        return [record]

    @classmethod
    def extract_origin(cls, record, origin):
        origin.name = record.get("name")
        return origin

    @classmethod
    def extract_country(cls, record, origin):
        country = HF.new_lbsn_record_with_id(
            lbsn.Country(),
            record.get('country_guid'),
            origin)
        set_lbsn_attr(country, "name", record)
        geom_center = record.get("geom_center")
        if geom_center:
            setattr(country, "geom_center", parse_geom(geom_center))
        geom_area = record.get("geom_area")
        if geom_area:
            setattr(country, "geom_area", parse_geom(geom_area))
        set_lbsn_attr(country, "url", record)
        set_lbsn_attr(country, "name_alternatives", record)
        return country

    @classmethod
    def extract_city(cls, record, origin):
        city = HF.new_lbsn_record_with_id(
            lbsn.City(),
            record.get('city_guid'),
            origin)
        set_lbsn_attr(city, "name", record)
        geom_center = record.get("geom_center")
        if geom_center:
            setattr(city, "geom_center", parse_geom(geom_center))
        geom_area = record.get("geom_area")
        if geom_area:
            setattr(city, "geom_area", parse_geom(geom_area))
        country_guid = record.get('country_guid')
        if country_guid:
            city.country_pkey.CopyFrom(
                HF.new_lbsn_record_with_id(
                    lbsn.Country(), record.get('country_guid'),
                    origin).pkey)
        set_lbsn_attr(city, "url", record)
        set_lbsn_attr(city, "name_alternatives", record)
        set_lbsn_attr(city, "sub_type", record)
        return city

    @classmethod
    def extract_place(cls, record, origin):
        place = HF.new_lbsn_record_with_id(
            lbsn.Place(),
            record.get('place_guid'),
            origin)
        set_lbsn_attr(place, "name", record)
        set_lbsn_attr(place, "post_count", record)
        set_lbsn_attr(place, "url", record)
        geom_center = record.get("geom_center")
        if geom_center:
            setattr(place, "geom_center", parse_geom(geom_center))
        geom_area = record.get("geom_area")
        if geom_area:
            setattr(place, "geom_area", parse_geom(geom_area))
        city_guid = record.get('city_guid')
        if city_guid:
            set_lbsn_pkey(
                place.city_pkey, lbsn.City(), record.get('city_guid'), origin)
        set_lbsn_attr(place, "name_alternatives", record)
        set_lbsn_attr(place, "place_description", record)
        set_lbsn_attr(place, "place_website", record)
        set_lbsn_attr(place, "place_phone", record)
        set_lbsn_attr(place, "address", record)
        set_lbsn_attr(place, "zip_code", record)
        set_lbsn_attr(place, "attributes", record)
        set_lbsn_attr(place, "checkin_count", record)
        set_lbsn_attr(place, "like_count", record)
        set_lbsn_attr(place, "parent_places", record)
        return place

    @classmethod
    def extract_usergroup(cls, record, origin):
        usergroup = HF.new_lbsn_record_with_id(
            lbsn.UserGroup(),
            record.get('usergroup_guid'),
            origin)
        usergroup.usergroup_name = record.get('usergroup_name')
        usergroup.usergroup_description = record.get('usergroup_description')
        usergroup.member_count = record.get('member_count')
        usergroup.usergroup_createdate = record.get('usergroup_createdate')
        usergroup.user_owner = record.get('user_owner')
        user_owner = record.get('user_owner')
        if user_owner:
            usergroup.user_owner_pkey.CopyFrom(
                HF.new_lbsn_record_with_id(
                    lbsn.User(), record.get('user_owner'),
                    origin).pkey)
        return usergroup

    @classmethod
    def extract_user(cls, record, origin):
        user = HF.new_lbsn_record_with_id(
            lbsn.User(),
            record.get('user_guid'),
            origin)
        set_lbsn_attr(user, "user_name", record)
        set_lbsn_attr(user, "user_fullname", record)
        set_lbsn_attr(user, "follows", record)
        set_lbsn_attr(user, "followed", record)
        set_lbsn_attr(user, "biography", record)
        set_lbsn_attr(user, "post_count", record)
        set_lbsn_attr(user, "url", record)
        set_lbsn_attr(user, "is_private", record)
        set_lbsn_attr(user, "is_available", record)

        lang = record.get('user_language')
        if lang:
            ref_user_language = lbsn.Language()
            ref_user_language.language_short = lang
            user.user_language.CopyFrom(ref_user_language)

        set_lbsn_attr(user, "user_location", record)
        user_location_geom = record.get("user_location_geom")
        if user_location_geom:
            setattr(user, "user_location_geom", parse_geom(user_location_geom))
        set_lbsn_attr(user, "liked_count", record)
        active_since = record.get('active_since')
        if active_since:
            copydate_lbsn_attr(
                user.active_since,
                active_since)
        set_lbsn_attr(user, "profile_image_url", record)
        set_lbsn_attr(user, "user_timezone", record)
        set_lbsn_attr(user, "user_utc_offset", record)
        set_lbsn_attr(user, "user_groups_member", record)
        set_lbsn_attr(user, "user_groups_follows", record)
        set_lbsn_attr(user, "group_count", record)
        return user

    @classmethod
    def extract_post(cls, record, origin):
        post = HF.new_lbsn_record_with_id(
            lbsn.Post(),
            record.get('post_guid'),
            origin)
        post_latlng = record.get("post_latlng")
        if post_latlng:
            setattr(post, "post_latlng", parse_geom(post_latlng))
        place_guid = record.get('place_guid')
        if place_guid:
            set_lbsn_pkey(
                post.place_pkey, lbsn.Place(),
                record.get('place_guid'), origin)
        city_guid = record.get('city_guid')
        if city_guid:
            set_lbsn_pkey(
                post.city_pkey, lbsn.City(),
                record.get('city_guid'), origin)
        country_guid = record.get('country_guid')
        if country_guid:
            set_lbsn_pkey(
                post.country_pkey, lbsn.Country(),
                record.get('country_guid'), origin)
        set_lbsn_pkey(
            post.user_pkey, lbsn.User(),
            record.get('user_guid'), origin)
        pub_date = record.get('post_publish_date')
        if pub_date:
            copydate_lbsn_attr(
                post.post_publish_date,
                pub_date)
        set_lbsn_attr(post, "post_body", record)
        post.post_geoaccuracy
        geo_acc = record.get("post_geoaccuracy")
        if geo_acc:
            # get enum value
            post.post_geoaccuracy = lbsn.Post.PostGeoaccuracy.Value(
                geo_acc.upper())
        set_lbsn_attr(post, "hashtags", record)
        set_lbsn_attr(post, "emoji", record)
        set_lbsn_attr(post, "post_like_count", record)
        set_lbsn_attr(post, "post_comment_count", record)
        set_lbsn_attr(post, "post_views_count", record)
        set_lbsn_attr(post, "post_title", record)
        crt_date = record.get('post_create_date')
        if crt_date:
            copydate_lbsn_attr(
                post.post_create_date,
                crt_date)
        set_lbsn_attr(post, "post_thumbnail_url", record)
        set_lbsn_attr(post, "post_url", record)
        post_type = record.get("post_type")
        if post_type:
            # get enum value
            post.post_type = lbsn.Post.PostType.Value(
                post_type.upper())
        set_lbsn_attr(post, "post_filter", record)
        set_lbsn_attr(post, "post_quote_count", record)
        set_lbsn_attr(post, "post_share_count", record)
        lang = record.get('post_language')
        if lang:
            ref_post_language = lbsn.Language()
            ref_post_language.language_short = lang
            post.post_language.CopyFrom(ref_post_language)
        set_lbsn_attr(post, "input_source", record)
        user_mentions = record.get("user_mentions")
        if user_mentions:
            mentioned_users_list = []
            for user_id in user_mentions:  # iterate over the list
                ref_user_record = \
                    HF.new_lbsn_record_with_id(
                        lbsn.User(), user_id, origin)
                mentioned_users_list.append(ref_user_record)
            post.user_mentions_pkey.extend(
                [user_ref.pkey for user_ref in mentioned_users_list])
        set_lbsn_attr(post, "post_content_license", record)
        return post

    @classmethod
    def extract_event(cls, record, origin):
        event = HF.new_lbsn_record_with_id(
            lbsn.Event(),
            record.get('event_guid'),
            origin)
        set_lbsn_attr(event, "name", record)
        event_latlng = record.get("event_latlng")
        if event_latlng:
            setattr(event, "event_latlng", parse_geom(event_latlng))
        event_area = record.get("event_area")
        if event_area:
            setattr(event, "event_area", parse_geom(event_area))
        set_lbsn_attr(event, "event_website", record)
        event_date = record.get('event_date')
        if event_date:
            copydate_lbsn_attr(
                event.event_date,
                event_date)
        event_date_start = record.get('event_date_start')
        if event_date_start:
            copydate_lbsn_attr(
                event.event_date_start,
                event_date_start)
        event_date_end = record.get('event_date_end')
        if event_date_end:
            copydate_lbsn_attr(
                event.event_date_end,
                event_date_end)
        duration = record.get('duration')
        if duration:
            copyduration_lbsn_attr(
                event.duration,
                duration)
        place_guid = record.get('place_guid')
        if place_guid:
            set_lbsn_pkey(
                event.place_pkey, lbsn.Place(),
                record.get('place_guid'), origin)
        city_guid = record.get('city_guid')
        if city_guid:
            set_lbsn_pkey(
                event.city_pkey, lbsn.City(),
                record.get('city_guid'), origin)
        country_guid = record.get('country_guid')
        if country_guid:
            set_lbsn_pkey(
                event.country_pkey, lbsn.Country(),
                record.get('country_guid'), origin)
        set_lbsn_pkey(
            event.user_pkey, lbsn.User(),
            record.get('user_guid'), origin)
        set_lbsn_attr(event, "event_description", record)
        set_lbsn_attr(event, "event_type", record)
        set_lbsn_attr(event, "event_share_count", record)
        set_lbsn_attr(event, "event_like_count", record)
        set_lbsn_attr(event, "event_comment_count", record)
        set_lbsn_attr(event, "event_views_count", record)
        set_lbsn_attr(event, "event_engage_count", record)
        return event

    @classmethod
    def extract_postreaction(cls, record):
        raise NotImplementedError(
            "Mapping of post reactions is not yet implemented")
