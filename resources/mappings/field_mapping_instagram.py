# -*- coding: utf-8 -*-

"""
Module for mapping Instagram (json) to common LBSN Structure.
"""

import json

# pylint: disable=no-member
import logging
import re
from typing import Any, Dict

import lbsnstructure as lbsn

from lbsntransform.tools.helper_functions import HelperFunctions as HF

MAPPING_ID = 14


class importer:
    """Provides mapping function from Instagram endpoints to
    protobuf lbsnstructure
    """

    ORIGIN_NAME = "Instagram"
    ORIGIN_ID = 1

    def __init__(
        self,
        ignore_non_geotagged=False,
        min_geoaccuracy=None,
        **_
    ):
        # Create the OriginID globally
        # this OriginID is required for all CompositeKeys
        origin = lbsn.Origin()
        origin.origin_id = lbsn.Origin.INSTAGRAM
        self.origin = origin
        # this is where all the data will be stored
        self.lbsn_records = []
        self.lbsn_relationships = []
        self.null_island = 0
        self.log = logging.getLogger("__main__")
        self.ignore_non_geotagged = ignore_non_geotagged
        self.min_geoaccuracy = min_geoaccuracy
        self.skipped_low_geoaccuracy = 0

    def get_skipped_geoaccuracy(self):
        """Get count of records skipped due to low geoaccuracy"""
        return self.skipped_low_geoaccuracy

    def parse_json_record(self, json_string_dict, *_):
        """Parse a standard Instagram json record"""
        # clear any records from previous run
        self.lbsn_records.clear()
        if json_string_dict is None:
            return
        json_data = json_string_dict.get("graphql")
        if json_data:
            place_json = json_data.get("location")
        else:
            # Assume Place without header
            place_json = json_string_dict
        if place_json is None:
            return self.lbsn_records
        place_record, country_ref_pkey, city_ref_pkey = self.extract_place(place_json)
        # postRecord.post_geoaccuracy = twitterPostAttributes.geoaccuracy
        self.lbsn_records.append(place_record)
        # extract posts
        post_node_list = place_json.get("edge_location_to_media").get("edges")
        if post_node_list:
            self.extract_posts(post_node_list, place_record)
        # extract top posts
        top_post_node_list = place_json.get("edge_location_to_top_posts").get("edges")
        if top_post_node_list:
            self.extract_posts(
                top_post_node_list, place_record, country_ref_pkey, city_ref_pkey
            )
        # finally, return list of all extracted records
        return self.lbsn_records

    def extract_posts(
        self,
        node_list,
        place_record: lbsn.Place = None,
        country_ref_pkey=None,
        city_ref_pkey=None,
    ):
        for post_node in node_list:
            json_string_dict = post_node.get("node")
            if json_string_dict:
                self.extract_post(
                    json_string_dict, place_record, country_ref_pkey, city_ref_pkey
                )

    def extract_user(self, json_string_dict):
        user = json_string_dict
        user_record = HF.new_lbsn_record_with_id(
            lbsn.User(), user.get("id"), self.origin
        )
        return user_record

    def extract_post(
        self,
        json_string_dict: Dict[str, Any],
        place_record: lbsn.Place = None,
        country_ref_pkey=None,
        city_ref_pkey=None,
    ):
        post_guid = json_string_dict.get("id")
        if not HF.check_notice_empty_post_guid(post_guid):
            return None
        post_record = HF.new_lbsn_record_with_id(lbsn.Post(), post_guid, self.origin)
        user_record = None
        user_info = json_string_dict.get("owner")
        if user_info:
            # Get Post/Reaction Details of User
            user_record = self.extract_user(user_info)
        if user_record:
            self.lbsn_records.append(user_record)
        else:
            self.log.warning(
                f"No User record found for post: {post_guid} "
                f"(post saved without userid).."
            )

        # Check from upstream to update post attrs
        if place_record:
            # assign place accuracy, by default
            post_record.post_geoaccuracy = lbsn.Post.PLACE
            post_record.place_pkey.CopyFrom(place_record.pkey)
            post_record.post_latlng = place_record.geom_center
        else:
            post_record.post_geoaccuracy = None
        # referenced country and city
        if city_ref_pkey:
            post_record.city_pkey.CopyFrom(city_ref_pkey)
        if country_ref_pkey:
            post_record.country_pkey.CopyFrom(country_ref_pkey)
        # if still no geoinformation, send post to Null-Island
        if not post_record.post_latlng:
            if self.ignore_non_geotagged is True:
                return None
            else:
                self.null_island += 1
                post_record.post_latlng = "POINT(%s %s)" % (0, 0)
        if self.min_geoaccuracy:
            if not HF.geoacc_within_threshold(
                post_record.post_geoaccuracy, self.min_geoaccuracy
            ):
                self.skipped_low_geoaccuracy += 1
                return
        post_record.post_publish_date.CopyFrom(
            HF.json_date_timestamp_to_proto(json_string_dict.get("taken_at_timestamp"))
        )
        if user_record:
            post_record.user_pkey.CopyFrom(user_record.pkey)

        def value_count(x):
            return 0 if x is None else x

        post_record.post_comment_count = value_count(
            json_string_dict.get("edge_media_to_comment").get("count")
        )
        post_record.post_like_count = value_count(
            json_string_dict.get("edge_liked_by").get("count")
        )
        post_shortcode = json_string_dict.get("shortcode")
        post_record.post_url = f"http://www.instagram.com/p/{post_shortcode}"
        if json_string_dict.get("thumbnail_src"):
            post_record.post_thumbnail_url = json_string_dict.get("thumbnail_src")
        post_caption_edge = json_string_dict.get("edge_media_to_caption")
        if post_caption_edge:
            post_caption_edge_edges = post_caption_edge.get("edges")
            if post_caption_edge_edges and not len(post_caption_edge_edges) == 0:
                post_caption = post_caption_edge["edges"][0]["node"]["text"]
                post_record.post_body = post_caption.replace("\n", " ").replace(
                    "\r", ""
                )
                hashtags = HF.extract_hashtags_from_string(post_caption)
                if hashtags:
                    for hashtag in hashtags:
                        post_record.hashtags.append(hashtag)
        is_video = json_string_dict.get("is_video")
        if is_video:
            post_record.post_type = lbsn.Post.VIDEO
            post_record.post_views_count = value_count(
                json_string_dict.get("video_view_count")
            )
        else:
            post_record.post_type = lbsn.Post.IMAGE
        post_record.emoji.extend(HF.extract_emoji(post_record.post_body))
        self.lbsn_records.append(post_record)

    def extract_place(self, postplace_json):
        place = postplace_json
        place_id = place.get("id")
        if not place_id:
            self.log.warning(f"No PlaceGuid\n\n{place}")
            input("Press Enter to continue... (entry will be skipped)")
            return
        lon_center = place.get("lng")
        lat_center = place.get("lat")
        if lon_center is None or lat_center is None:
            # assign place to Null Island
            lon_center = 0
            lat_center = 0
            self.log.info(f"Empty lat or lng: Location {place_id}")
        # place_guid
        # For POIs, City is not available on Twitter
        place_record = HF.new_lbsn_record_with_id(lbsn.Place(), place_id, self.origin)
        place_record.geom_center = "POINT(%s %s)" % (lon_center, lat_center)
        place_name = place.get("name").replace("\n\r", "")
        # for some reason, twitter place entities sometimes contain
        # linebreaks or whitespaces. We don't want this.
        place_name = place.get("name").replace("\n\r", "")
        # remove multiple whitespace
        place_name = re.sub(" +", " ", place_name)
        place_record.name = place_name
        place_slug = place.get("slug")
        if place_slug:
            place_record.url = (
                f"https://www.instagram.com/explore/locations/"
                f"{place_id}/{place_slug}"
            )
        place_record.place_website = place.get("website")
        place_record.place_description = place.get("blurb")
        place_record.place_phone = place.get("phone")
        address_string = place.get("address_json")
        if address_string:
            address_json = json.loads(address_string)
            place_adr_street = address_json.get("street_address")
            place_zip_code = address_json.get("zip_code")
            place_city_name = address_json.get("city_name")
            place_region_name = address_json.get("region_name")
            place_country_name = address_json.get("US")
            place_record.address = ", ".join(
                filter(
                    None,
                    (
                        place_adr_street,
                        place_city_name,
                        place_region_name,
                        place_country_name,
                    ),
                )
            )
            place_record.zip_code = place_zip_code
        # extract directory
        directory_json = place.get("directory")
        if directory_json:
            country_json = directory_json.get("country")
            if country_json:
                cid = country_json.get("id")
                slug = country_json.get("slug")
                ref_country_record = HF.new_lbsn_record_with_id(
                    lbsn.Country(), cid, self.origin
                )
                ref_country_record.name = country_json.get("name")
                ref_country_record.url = (
                    f"https://www.instagram.com/explore/locations/{cid}/{slug}"
                )
                self.lbsn_records.append(ref_country_record)
            city_json = directory_json.get("city")
            if city_json:
                cid = city_json.get("id")
                slug = city_json.get("slug")
                ref_city_record = HF.new_lbsn_record_with_id(
                    lbsn.City(), cid, self.origin
                )
                ref_city_record.name = city_json.get("name")
                ref_city_record.url = (
                    f"https://www.instagram.com/explore/locations/{cid}/{slug}"
                )
                ref_city_record.country_pkey.CopyFrom(ref_country_record.pkey)
                self.lbsn_records.append(ref_city_record)
                place_record.city_pkey.CopyFrom(ref_city_record.pkey)
        country_ref_pkey = None
        if directory_json and country_json:
            country_ref_pkey = ref_country_record.pkey
        city_ref_pkey = None
        if directory_json and city_json:
            city_ref_pkey = ref_city_record.pkey
        return place_record, country_ref_pkey, city_ref_pkey
