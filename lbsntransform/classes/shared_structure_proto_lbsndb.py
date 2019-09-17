# -*- coding: utf-8 -*-

"""
Shared structure and mapping between DB and Proto LBSN Structure.
"""

# pylint: disable=no-member

import sys

from lbsnstructure.lbsnstructure_pb2 import (City, Country, Place,
                                             Post, PostReaction,
                                             Relationship, User,
                                             UserGroup)

from .helper_functions import HelperFunctions as HF


class ProtoLBSNMapping():
    """ Methods to map ProtoBuf structure to PG SQL structure."""

    @staticmethod
    def get_header_for_type(desc_name):
        """ Will return lbsn-db headers for proto buf record types

        - in correct order
        - ready for copy-from pg import
        """
        dict_switcher = \
            {City.DESCRIPTOR.name:
             'origin_id, city_guid, name, name_alternatives, geom_center, '
             'geom_area, url, country_guid, sub_type',
             Country.DESCRIPTOR.name:
             'origin_id, country_guid, name, name_alternatives, geom_center, '
             'geom_area, url',
             Place.DESCRIPTOR.name:
             'origin_id, place_guid, name, name_alternatives, geom_center, '
             'geom_area, url, city_guid, post_count, place_description, '
             'place_website, place_phone, address, zip_code, attributes, '
             'checkin_count, like_count, parent_places',
             Post.DESCRIPTOR.name:
             'origin_id, post_guid, post_latlng, place_guid, city_guid, '
             'country_guid, post_geoaccuracy, user_guid, post_create_date, '
             'post_publish_date, post_body, post_language, user_mentions, '
             'hashtags, emoji, post_like_count, post_comment_count, '
             'post_views_count, post_title, post_thumbnail_url, post_url, '
             'post_type, post_filter, post_quote_count, post_share_count, '
             'input_source, post_content_license',
             PostReaction.DESCRIPTOR.name:
             'origin_id, reaction_guid, reaction_latlng, user_guid, '
             'referencedPost_guid, referencedPostreaction_guid, '
             'reaction_type, reaction_date, reaction_content, '
             'reaction_like_count, user_mentions',
             User.DESCRIPTOR.name:
             'origin_id, user_guid, user_name, user_fullname, follows, '
             'followed, group_count, biography, post_count, is_private, '
             'url, is_available, user_language, user_location, '
             'user_location_geom, liked_count, active_since, '
             'profile_image_url, user_timezone, user_utc_offset, '
             'user_groups_member, user_groups_follows',
             UserGroup.DESCRIPTOR.name:
             'origin_id, usergroup_guid, usergroup_name, '
             'usergroup_description, member_count, '
             'usergroup_createdate, user_owner',
             '_user_mentions_user':
             'origin_id, user_guid, mentioneduser_guid',
             '_user_follows_group':
             'origin_id, user_guid, group_guid',
             '_user_memberof_group':
             'origin_id, user_guid, group_guid',
             '_user_connectsto_user':
             'origin_id, user_guid, connectedto_user_guid',
             '_user_friends_user':
             'origin_id, user_guid, friend_guid'
             }
        return dict_switcher.get(desc_name)

    def func_prepare_selector(self, record):
        """Select correct prepare function according to record type"""
        dict_switcher = {
            Country().DESCRIPTOR.name: self.prepare_lbsn_country,
            City().DESCRIPTOR.name: self.prepare_lbsn_city,
            Place().DESCRIPTOR.name: self.prepare_lbsn_place,
            User().DESCRIPTOR.name: self.prepare_lbsn_user,
            UserGroup().DESCRIPTOR.name: self.prepare_lbsn_usergroup,
            Post().DESCRIPTOR.name: self.prepare_lbsn_post,
            PostReaction().DESCRIPTOR.name: self.prepare_lbsn_postreaction,
            Relationship().DESCRIPTOR.name: self.prepare_lbsn_relation
        }
        prepare_function = dict_switcher.get(record.DESCRIPTOR.name)
        return prepare_function(record)

    def prepare_lbsn_country(self, record):
        """Get common attributes for records of type Place"""
        place_record = PlaceBaseAttrShared(record)
        prepared_record = (place_record.origin_id,
                           place_record.guid,
                           place_record.name,
                           place_record.name_alternatives,
                           HF.return_ewkb_from_geotext(
                               place_record.geom_center),
                           HF.return_ewkb_from_geotext(place_record.geom_area),
                           place_record.url)
        return prepared_record

    def prepare_lbsn_city(self, record):
        """Get common attributes for records of type City"""
        place_record = PlaceBaseAttrShared(record)
        country_guid = HF.null_check(record.country_pkey.id)
        sub_type = HF.null_check(record.sub_type)
        prepared_record = (place_record.origin_id,
                           place_record.guid,
                           place_record.name,
                           place_record.name_alternatives,
                           HF.return_ewkb_from_geotext(
                               place_record.geom_center),
                           HF.return_ewkb_from_geotext(
                               place_record.geom_area),
                           place_record.url,
                           country_guid,
                           sub_type)
        return prepared_record

    def prepare_lbsn_place(self, record):
        """Get common attributes for records of type Place"""
        place_record = PlaceBaseAttrShared(record)
        # get additional attributes specific to places
        city_guid = HF.null_check(record.city_pkey.id)
        post_count = HF.null_check(record.post_count)
        place_description = HF.null_check(record.place_description)
        place_website = HF.null_check(record.place_website)
        place_phone = HF.null_check(record.place_phone)
        address = HF.null_check(record.address)
        zip_code = HF.null_check(record.zip_code)
        attributes = HF.map_to_dict(HF.null_check(record.attributes))
        checkin_count = HF.null_check(record.checkin_count)
        like_count = HF.null_check(record.like_count)
        parent_places = HF.null_check(record.parent_places)
        prepared_record = (place_record.origin_id,
                           place_record.guid,
                           place_record.name,
                           place_record.name_alternatives,
                           HF.return_ewkb_from_geotext(
                               place_record.geom_center),
                           HF.return_ewkb_from_geotext(
                               place_record.geom_area),
                           place_record.url,
                           city_guid,
                           post_count,
                           place_description,
                           place_website,
                           place_phone,
                           address,
                           zip_code,
                           attributes,
                           checkin_count,
                           like_count,
                           parent_places)
        return prepared_record

    def prepare_lbsn_user(self, record):
        """Get common attributes for records of type User"""
        user_record = UserAttrShared(record)
        prepared_record = (user_record.origin_id,
                           user_record.guid,
                           user_record.user_name,
                           user_record.user_fullname,
                           user_record.follows,
                           user_record.followed,
                           user_record.group_count,
                           user_record.biography,
                           user_record.post_count,
                           user_record.is_private,
                           user_record.url,
                           user_record.is_available,
                           user_record.user_language,
                           user_record.user_location,
                           HF.return_ewkb_from_geotext(
                               user_record.user_location_geom),
                           user_record.liked_count,
                           user_record.active_since,
                           user_record.profile_image_url,
                           user_record.user_timezone,
                           user_record.user_utc_offset,
                           user_record.user_groups_member,
                           user_record.user_groups_follows)
        return prepared_record

    def prepare_lbsn_usergroup(self, record):
        """Get common attributes for records of type Userroup"""
        user_group_record = UsergroupAttrShared(record)
        prepared_record = (user_group_record.origin_id,
                           user_group_record.guid,
                           user_group_record.usergroup_name,
                           user_group_record.usergroup_description,
                           user_group_record.member_count,
                           user_group_record.usergroup_createdate,
                           user_group_record.user_owner)
        return prepared_record

    def prepare_lbsn_post(self, record):
        """Get common attributes for records of type Post"""
        post_record = PostAttrShared(record)
        prepared_record = (post_record.origin_id,
                           post_record.guid,
                           HF.return_ewkb_from_geotext(
                               post_record.post_latlng),
                           post_record.place_guid,
                           post_record.city_guid,
                           post_record.country_guid,
                           post_record.post_geoaccuracy,
                           post_record.user_guid,
                           post_record.post_create_date,
                           post_record.post_publish_date,
                           post_record.post_body,
                           post_record.post_language,
                           post_record.user_mentions,
                           post_record.hashtags,
                           post_record.emoji,
                           post_record.post_like_count,
                           post_record.post_comment_count,
                           post_record.post_views_count,
                           post_record.post_title,
                           post_record.post_thumbnail_url,
                           post_record.post_url,
                           post_record.post_type,
                           post_record.post_filter,
                           post_record.post_quote_count,
                           post_record.post_share_count,
                           post_record.input_source,
                           post_record.post_content_license)
        return prepared_record

    def prepare_lbsn_postreaction(self, record):
        """Get common attributes for records of type PostReaction"""
        post_reaction_record = PostreactionAttrShared(record)
        prepared_record = (post_reaction_record.origin_id,
                           post_reaction_record.guid,
                           HF.return_ewkb_from_geotext(
                               post_reaction_record.reaction_latlng),
                           post_reaction_record.user_guid,
                           post_reaction_record.referenced_post,
                           post_reaction_record.referenced_postreaction,
                           post_reaction_record.reaction_type,
                           post_reaction_record.reaction_date,
                           post_reaction_record.reaction_content,
                           post_reaction_record.reaction_like_count,
                           post_reaction_record.user_mentions)
        return prepared_record

    def prepare_lbsn_relation(self, record):
        """Get common attributes for records of type lbsn Relation"""
        relations_record = RelationAttrShared(record)
        prepared_typerecord_tuple = \
            (relations_record.rel_type,
             self.prepareRecordValues(relations_record.origin_id,
                                      relations_record.guid,
                                      relations_record.guid_rel))
        return prepared_typerecord_tuple


class PlaceBaseAttrShared():
    """Shared structure for Place Attributes

    Contains attributes shared among PG DB and LBSN ProtoBuf spec.
    Note that Country, City and Place have the same structure.
    """

    def __init__(self, record=None):
        if record is None:
            record = Place()  # init empty structure
        self.origin_id = record.pkey.origin.origin_id  # = 3
        self.guid = record.pkey.id
        self.name = HF.null_check(record.name)
        # because ProtoBuf Repeated Field does not support distinct rule,
        # we remove any duplicates in list fields prior to submission here
        self.name_alternatives = list(set(record.name_alternatives))
        if self.name and self.name in self.name_alternatives:
            self.name_alternatives.remove(self.name)
        self.url = HF.null_check(record.url)
        self.geom_center = HF.null_check(record.geom_center)
        self.geom_area = HF.null_check(record.geom_area)


class UserAttrShared():
    """Shared structure for User Attributes

    Contains attributes shared among PG DB and LBSN ProtoBuf spec.
    """

    def __init__(self, record=None):
        if record is None:
            record = User()
        self.origin_id = record.pkey.origin.origin_id
        self.guid = record.pkey.id
        self.user_name = HF.null_check(record.user_name)
        self.user_fullname = HF.null_check(record.user_fullname)
        self.follows = HF.null_check(record.follows)
        self.followed = HF.null_check(record.followed)
        self.group_count = HF.null_check(record.group_count)
        self.biography = HF.null_check(record.biography)
        self.post_count = HF.null_check(record.post_count)
        self.url = HF.null_check(record.url)
        self.is_private = HF.null_check(record.is_private)
        self.is_available = HF.null_check(record.is_available)
        self.user_language = HF.null_check(record.user_language.language_short)
        self.user_location = HF.null_check(record.user_location)
        self.user_location_geom = HF.null_check(record.user_location_geom)
        self.liked_count = HF.null_check(record.liked_count)
        self.active_since = HF.null_check_datetime(record.active_since)
        self.profile_image_url = HF.null_check(record.profile_image_url)
        self.user_timezone = HF.null_check(record.user_timezone)
        self.user_utc_offset = HF.null_check(record.user_utc_offset)
        self.user_groups_member = list(set(record.user_groups_member))
        self.user_groups_follows = list(set(record.user_groups_follows))


class UsergroupAttrShared():
    """Shared structure for Usergroup Attributes

    Contains attributes shared among PG DB and LBSN ProtoBuf spec.
    """

    def __init__(self, record=None):
        if record is None:
            record = UserGroup()
        self.origin_id = record.pkey.origin.origin_id
        self.guid = record.pkey.id
        self.usergroup_name = HF.null_check(record.usergroup_name)
        self.usergroup_description = HF.null_check(
            record.usergroup_description)
        self.member_count = HF.null_check(record.member_count)
        self.usergroup_createdate = HF.null_check_datetime(
            record.usergroup_createdate)
        self.user_owner = HF.null_check(record.user_owner_pkey.id)


class PostAttrShared():
    """Shared structure for Post Attributes

    Contains attributes shared among PG DB and LBSN ProtoBuf spec.
    """

    def __init__(self, record=None):
        if record is None:
            record = Post()

        self.origin_id = record.pkey.origin.origin_id
        self.guid = record.pkey.id
        self.post_latlng = HF.null_geom_check(record.post_latlng)
        self.place_guid = HF.null_check(record.place_pkey.id)
        self.city_guid = HF.null_check(record.city_pkey.id)
        self.country_guid = HF.null_check(record.country_pkey.id)
        self.post_geoaccuracy = HF.turn_lower(HF.null_check(
            Post().PostGeoaccuracy.Name(record.post_geoaccuracy)))
        self.user_guid = HF.null_check(record.user_pkey.id)
        self.post_create_date = HF.null_check_datetime(record.post_create_date)
        self.post_publish_date = HF.null_check_datetime(
            record.post_publish_date)
        self.post_body = HF.null_check(record.post_body)
        self.post_language = HF.null_check(record.post_language.language_short)
        self.user_mentions = list(
            set([pkey.id for pkey in record.user_mentions_pkey]))
        self.hashtags = list(set(record.hashtags))
        self.emoji = list(set(record.emoji))
        self.post_like_count = HF.null_check(record.post_like_count)
        self.post_comment_count = HF.null_check(record.post_comment_count)
        self.post_views_count = HF.null_check(record.post_views_count)
        self.post_title = HF.null_check(record.post_title)
        self.post_thumbnail_url = HF.null_check(record.post_thumbnail_url)
        self.post_url = HF.null_check(record.post_url)
        self.post_type = HF.turn_lower(HF.null_check(
            Post().PostType.Name(record.post_type)))
        self.post_filter = HF.null_check(record.post_filter)
        self.post_quote_count = HF.null_check(record.post_quote_count)
        self.post_share_count = HF.null_check(record.post_share_count)
        self.input_source = HF.null_check(record.input_source)
        self.post_content_license = HF.null_check(record.post_content_license)
        # optional:
        self.latitude = 0
        self.longitude = 0


class PostreactionAttrShared():
    """Shared structure for Postreaction Attributes

    Contains attributes shared among PG DB and LBSN ProtoBuf spec.
    """

    def __init__(self, record=None):
        if record is None:
            record = PostReaction()
        self.origin_id = record.pkey.origin.origin_id
        self.guid = record.pkey.id
        self.reaction_latlng = HF.null_geom_check(record.reaction_latlng)
        self.user_guid = HF.null_check(record.user_pkey.id)
        self.referenced_post = HF.null_check(record.referencedPost_pkey.id)
        self.referenced_postreaction = HF.null_check(
            record.referencedPostreaction_pkey.id)
        self.reaction_type = HF.turn_lower(HF.null_check(
            PostReaction().ReactionType.Name(record.reaction_type)))
        self.reaction_date = HF.null_check_datetime(record.reaction_date)
        self.reaction_content = HF.null_check(record.reaction_content)
        self.reaction_like_count = HF.null_check(record.reaction_like_count)
        self.user_mentions = list(
            set([pkey.id for pkey in record.user_mentions_pkey]))


class RelationAttrShared():
    """Shared structure for Relation Attributes

    Contains attributes shared among PG DB and LBSN ProtoBuf spec.
    """

    def __init__(self, relationship=None):
        if relationship is None:
            relationship = Relationship()
        self.origin_id = relationship.pkey.relation_to.origin.origin_id
        self.guid = relationship.pkey.relation_to.id
        self.guid_rel = relationship.pkey.relation_from.id
        self.rel_type = HF.null_check(Relationship().RelationshipType.Name(
            relationship.relationship_type)).lower()
