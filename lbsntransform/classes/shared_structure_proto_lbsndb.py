# -*- coding: utf-8 -*-

from lbsnstructure.lbsnstructure_pb2 import *
from .helper_functions import HelperFunctions

class ProtoLBSM_db_Mapping():
    def get_header_for_type(desc_name):
        """ Will return lbsn-db headers for proto buf record types
        """
        dict_switcher = {lbsnCity.DESCRIPTOR.name: 'origin_id, city_guid, name, name_alternatives, geom_center, geom_area, url, country_guid, sub_type',
                                    lbsnCountry.DESCRIPTOR.name: 'origin_id, country_guid, name, name_alternatives, geom_center, geom_area, url',
                                    lbsnPlace.DESCRIPTOR.name: 'origin_id, place_guid, name, name_alternatives, geom_center, geom_area, url, city_guid, post_count',
                                    lbsnPost.DESCRIPTOR.name: 'origin_id, post_guid, post_latlng, place_guid, city_guid, country_guid, post_geoaccuracy, user_guid, post_create_date, post_publish_date, post_body, post_language, user_mentions, hashtags, emoji, post_like_count, post_comment_count, post_views_count, post_title, post_thumbnail_url, post_url, post_type, post_filter, post_quote_count, post_share_count, input_source',
                                    lbsnPostReaction.DESCRIPTOR.name: 'origin_id, reaction_guid, reaction_latlng, user_guid, referencedPost_guid, referencedPostreaction_guid, reaction_type, reaction_date, reaction_content, reaction_like_count, user_mentions',
                                    lbsnUser.DESCRIPTOR.name: 'origin_id, user_guid, user_name, user_fullname, follows, followed, group_count, biography, post_count, is_private, url, is_available, user_language, user_location, user_location_geom, liked_count, active_since, profile_image_url, user_timezone, user_utc_offset, user_groups_member, user_groups_follows',
                                    lbsnUserGroup.DESCRIPTOR.name: 'origin_id, usergroup_guid, usergroup_name, usergroup_description, member_count, usergroup_createdate, user_owner',
                                    '_user_mentions_user': 'origin_id, user_guid, mentioneduser_guid',
                                    '_user_follows_group': 'origin_id, user_guid, group_guid',
                                    '_user_memberof_group': 'origin_id, user_guid, group_guid',
                                    '_user_connectsto_user': 'origin_id, user_guid, connectedto_user_guid',
                                    '_user_friends_user': 'origin_id, user_guid, friend_guid'
                               }
        return dict_switcher.get(desc_name)

    def func_prepare_selector(self, record):
        dictSwitcher = {
            lbsnCountry().DESCRIPTOR.name: self.prepareLbsnCountry,
            lbsnCity().DESCRIPTOR.name: self.prepareLbsnCity,
            lbsnPlace().DESCRIPTOR.name: self.prepareLbsnPlace,
            lbsnUser().DESCRIPTOR.name: self.prepareLbsnUser,
            lbsnUserGroup().DESCRIPTOR.name: self.prepareLbsnUserGroup,
            lbsnPost().DESCRIPTOR.name: self.prepareLbsnPost,
            lbsnPostReaction().DESCRIPTOR.name: self.prepareLbsnPostReaction,
            lbsnRelationship().DESCRIPTOR.name: self.prepareLbsnRelationship
        }
        prepareFunction = dictSwitcher.get(record.DESCRIPTOR.name)
        return prepareFunction(record)

    def prepareLbsnCountry(self, record):
        # Get common attributes for place types Place, City and Country
        placeRecord = placeAttrShared(record)
        preparedRecord = (placeRecord.OriginID,
                          placeRecord.Guid,
                          placeRecord.name,
                          placeRecord.name_alternatives,
                          HelperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_center),
                          HelperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_area),
                          placeRecord.url)
        return preparedRecord

    def prepareLbsnCity(self, record):
        placeRecord = placeAttrShared(record)
        countryGuid = HelperFunctions.null_check(record.country_pkey.id)
        subType = HelperFunctions.null_check(record.sub_type)
        preparedRecord = (placeRecord.OriginID,
                          placeRecord.Guid,
                          placeRecord.name,
                          placeRecord.name_alternatives,
                          HelperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_center),
                          HelperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_area),
                          placeRecord.url,
                          countryGuid,
                          subType)
        return preparedRecord

    def prepareLbsnPlace(self, record):
        placeRecord = placeAttrShared(record)
        cityGuid = HelperFunctions.null_check(record.city_pkey.id)
        postCount = HelperFunctions.null_check(record.post_count)
        preparedRecord = (placeRecord.OriginID,
                          placeRecord.Guid,
                          placeRecord.name,
                          placeRecord.name_alternatives,
                          HelperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_center),
                          HelperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_area),
                          placeRecord.url,
                          cityGuid,
                          postCount)
        return preparedRecord

    def prepareLbsnUser(self, record):
        userRecord = userAttrShared(record)
        preparedRecord = (userRecord.OriginID,
                          userRecord.Guid,
                          userRecord.user_name,
                          userRecord.user_fullname,
                          userRecord.follows,
                          userRecord.followed,
                          userRecord.group_count,
                          userRecord.biography,
                          userRecord.post_count,
                          userRecord.is_private,
                          userRecord.url,
                          userRecord.is_available,
                          userRecord.user_language,
                          userRecord.user_location,
                          HelperFunctions.returnEWKBFromGeoTEXT(userRecord.user_location_geom),
                          userRecord.liked_count,
                          userRecord.active_since,
                          userRecord.profile_image_url,
                          userRecord.user_timezone,
                          userRecord.user_utc_offset,
                          userRecord.user_groups_member,
                          userRecord.user_groups_follows)
        return preparedRecord

    def prepareLbsnUserGroup(self, record):
        userGroupRecord = userGroupAttrShared(record)
        preparedRecord = (userGroupRecord.OriginID,
                          userGroupRecord.Guid,
                          userGroupRecord.usergroup_name,
                          userGroupRecord.usergroup_description,
                          userGroupRecord.member_count,
                          userGroupRecord.usergroup_createdate,
                          userGroupRecord.user_owner)
        return preparedRecord

    def prepareLbsnPost(self, record):
        postRecord = postAttrShared(record)
        preparedRecord = (postRecord.OriginID,
                          postRecord.Guid,
                          HelperFunctions.returnEWKBFromGeoTEXT(postRecord.post_latlng),
                          postRecord.place_guid,
                          postRecord.city_guid,
                          postRecord.country_guid,
                          postRecord.post_geoaccuracy,
                          postRecord.user_guid,
                          postRecord.post_create_date,
                          postRecord.post_publish_date,
                          postRecord.post_body,
                          postRecord.post_language,
                          postRecord.user_mentions,
                          postRecord.hashtags,
                          postRecord.emoji,
                          postRecord.post_like_count,
                          postRecord.post_comment_count,
                          postRecord.post_views_count,
                          postRecord.post_title,
                          postRecord.post_thumbnail_url,
                          postRecord.post_url,
                          postRecord.post_type,
                          postRecord.post_filter,
                          postRecord.post_quote_count,
                          postRecord.post_share_count,
                          postRecord.input_source)
        return preparedRecord

    def prepareLbsnPostReaction(self, record):
        postReactionRecord = postReactionAttrShared(record)
        preparedRecord = (postReactionRecord.OriginID,
                          postReactionRecord.Guid,
                          HelperFunctions.returnEWKBFromGeoTEXT(postReactionRecord.reaction_latlng),
                          postReactionRecord.user_guid,
                          postReactionRecord.referencedPost,
                          postReactionRecord.referencedPostreaction,
                          postReactionRecord.reaction_type,
                          postReactionRecord.reaction_date,
                          postReactionRecord.reaction_content,
                          postReactionRecord.reaction_like_count,
                          postReactionRecord.user_mentions)
        return preparedRecord

    def prepareLbsnRelationship(self, record):
        relationshipRecord = relationshipAttrShared(record)
        preparedTypeRecordTuple = (relationshipRecord.relType,
                          self.prepareRecordValues(relationshipRecord.OriginID,
                          relationshipRecord.Guid,
                          relationshipRecord.Guid_Rel))
        return preparedTypeRecordTuple

class placeAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id # = 3
        self.Guid = record.pkey.id
        self.name = HelperFunctions.null_check(record.name)
        # because ProtoBuf Repeated Field does not support distinct rule, we remove any duplicates in list fields prior to submission here
        self.name_alternatives = list(set(record.name_alternatives))
        if self.name and self.name in self.name_alternatives:
            self.name_alternatives.remove(self.name)
        self.url = HelperFunctions.null_check(record.url)
        self.geom_center = HelperFunctions.null_check(record.geom_center)
        self.geom_area = HelperFunctions.null_check(record.geom_area)

class userAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.user_name = HelperFunctions.null_check(record.user_name)
        self.user_fullname = HelperFunctions.null_check(record.user_fullname)
        self.follows = HelperFunctions.null_check(record.follows)
        self.followed = HelperFunctions.null_check(record.followed)
        self.group_count = HelperFunctions.null_check(record.group_count)
        self.biography = HelperFunctions.null_check(record.biography)
        self.post_count = HelperFunctions.null_check(record.post_count)
        self.url = HelperFunctions.null_check(record.url)
        self.is_private = HelperFunctions.null_check(record.is_private)
        self.is_available = HelperFunctions.null_check(record.is_available)
        self.user_language = HelperFunctions.null_check(record.user_language.language_short)
        self.user_location = HelperFunctions.null_check(record.user_location)
        self.user_location_geom = HelperFunctions.null_check(record.user_location_geom)
        self.liked_count = HelperFunctions.null_check(record.liked_count)
        self.active_since = HelperFunctions.null_check_datetime(record.active_since)
        self.profile_image_url = HelperFunctions.null_check(record.profile_image_url)
        self.user_timezone = HelperFunctions.null_check(record.user_timezone)
        self.user_utc_offset = HelperFunctions.null_check(record.user_utc_offset)
        self.user_groups_member = list(set(record.user_groups_member))
        self.user_groups_follows = list(set(record.user_groups_follows))

class userGroupAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.usergroup_name = HelperFunctions.null_check(record.usergroup_name)
        self.usergroup_description = HelperFunctions.null_check(record.usergroup_description)
        self.member_count = HelperFunctions.null_check(record.member_count)
        self.usergroup_createdate = HelperFunctions.null_check_datetime(record.usergroup_createdate)
        self.user_owner = HelperFunctions.null_check(record.user_owner_pkey.id)

class postAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.post_latlng = HelperFunctions.null_check(record.post_latlng)
        self.place_guid = HelperFunctions.null_check(record.place_pkey.id)
        self.city_guid = HelperFunctions.null_check(record.city_pkey.id)
        self.country_guid = HelperFunctions.null_check(record.country_pkey.id)
        self.post_geoaccuracy = HelperFunctions.null_check(lbsnPost().PostGeoaccuracy.Name(record.post_geoaccuracy)).lower()
        self.user_guid = HelperFunctions.null_check(record.user_pkey.id)
        self.post_create_date = HelperFunctions.null_check_datetime(record.post_create_date)
        self.post_publish_date = HelperFunctions.null_check_datetime(record.post_publish_date)
        self.post_body = HelperFunctions.null_check(record.post_body)
        self.post_language = HelperFunctions.null_check(record.post_language.language_short)
        self.user_mentions = list(set([pkey.id for pkey in record.user_mentions_pkey]))
        self.hashtags = list(set(record.hashtags))
        self.emoji = list(set(record.emoji))
        self.post_like_count = HelperFunctions.null_check(record.post_like_count)
        self.post_comment_count = HelperFunctions.null_check(record.post_comment_count)
        self.post_views_count = HelperFunctions.null_check(record.post_views_count)
        self.post_title = HelperFunctions.null_check(record.post_title)
        self.post_thumbnail_url = HelperFunctions.null_check(record.post_thumbnail_url)
        self.post_url = HelperFunctions.null_check(record.post_url)
        self.post_type = HelperFunctions.null_check(lbsnPost().PostType.Name(record.post_type)).lower()
        self.post_filter = HelperFunctions.null_check(record.post_filter)
        self.post_quote_count = HelperFunctions.null_check(record.post_quote_count)
        self.post_share_count = HelperFunctions.null_check(record.post_share_count)
        self.input_source = HelperFunctions.null_check(record.input_source)

class postReactionAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.reaction_latlng = HelperFunctions.null_check(record.reaction_latlng)
        self.user_guid = HelperFunctions.null_check(record.user_pkey.id)
        self.referencedPost = HelperFunctions.null_check(record.referencedPost_pkey.id)
        self.referencedPostreaction = HelperFunctions.null_check(record.referencedPostreaction_pkey.id)
        self.reaction_type = HelperFunctions.null_check(lbsnPostReaction().ReactionType.Name(record.reaction_type)).lower()
        self.reaction_date = HelperFunctions.null_check_datetime(record.reaction_date)
        self.reaction_content = HelperFunctions.null_check(record.reaction_content)
        self.reaction_like_count = HelperFunctions.null_check(record.reaction_like_count)
        self.user_mentions = list(set([pkey.id for pkey in record.user_mentions_pkey]))

class relationshipAttrShared():
    def __init__(self, relationship):
        self.OriginID = relationship.pkey.relation_to.origin.origin_id
        self.Guid = relationship.pkey.relation_to.id
        self.Guid_Rel = relationship.pkey.relation_from.id
        self.relType = HelperFunctions.null_check(lbsnRelationship().RelationshipType.Name(relationship.relationship_type)).lower()