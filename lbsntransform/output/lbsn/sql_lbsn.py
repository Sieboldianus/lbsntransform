# -*- coding: utf-8 -*-

"""
Module for sql insert functions for LBSN (raw) db
"""

from lbsnstructure import lbsnstructure_pb2 as lbsn
from lbsntransform.tools.helper_functions import HelperFunctions as HF

from lbsntransform.output.lbsn.shared_structure_proto_lbsndb import ProtoLBSNMapping


class LBSNSql():
    """Maps LBSN Types to raw SQL Structure"""

    DB_MAPPING = ProtoLBSNMapping()

    @classmethod
    def type_sql_mapper(cls):
        """Assigns record types to SQL Insert SQLs"""
        type_sql_mapping = {
            lbsn.Origin().DESCRIPTOR.name: cls.origin_insertsql,
            lbsn.Country().DESCRIPTOR.name: cls.country_insertsql,
            lbsn.City().DESCRIPTOR.name: cls.city_insertsql,
            lbsn.Place().DESCRIPTOR.name: cls.place_insertsql,
            lbsn.User().DESCRIPTOR.name: cls.user_insertsql,
            lbsn.UserGroup().DESCRIPTOR.name: cls.usergroup_insertsql,
            lbsn.Post().DESCRIPTOR.name: cls.post_insertsql,
            lbsn.Event().DESCRIPTOR.name: cls.event_insertsql,
            lbsn.PostReaction().DESCRIPTOR.name: cls.postreaction_insertsql,
        }
        return type_sql_mapping

    @staticmethod
    def origin_insertsql(values_str: str, record_type):
        """SQL and value injection for lbsn.City"""
        insert_sql = \
            f'''
            INSERT INTO social."origin" (
                {LBSNSql.DB_MAPPING.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id)
            DO UPDATE SET
                name = EXCLUDED.name;
            '''
        return insert_sql

    @staticmethod
    def postreaction_insertsql(values_str: str, record_type):
        """SQL and value injection for lbsn.PostReaction"""
        insert_sql = \
            f'''
            INSERT INTO topical."post_reaction" (
                {LBSNSql.DB_MAPPING.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id, reaction_guid)
            DO UPDATE SET
                reaction_latlng = COALESCE(
                    NULLIF(EXCLUDED.reaction_latlng,
                    '{HF.NULL_GEOM_HEX}'),
                    topical."post_reaction".reaction_latlng,
                    '{HF.NULL_GEOM_HEX}'),
                user_guid = COALESCE(EXCLUDED.user_guid,
                    topical."post_reaction".user_guid),
                referencedPost_guid = COALESCE(EXCLUDED.referencedPost_guid,
                    topical."post_reaction".referencedPost_guid),
                referencedPostreaction_guid = COALESCE(
                    EXCLUDED.referencedPostreaction_guid,
                    topical."post_reaction".referencedPostreaction_guid),
                reaction_type = COALESCE(NULLIF(EXCLUDED.reaction_type, 'unknown'),
                    topical."post_reaction".reaction_type, 'unknown'),
                reaction_date = COALESCE(EXCLUDED.reaction_date,
                    topical."post_reaction".reaction_date),
                reaction_content = COALESCE(EXCLUDED.reaction_content,
                    topical."post_reaction".reaction_content),
                reaction_like_count = COALESCE(EXCLUDED.reaction_like_count,
                    topical."post_reaction".reaction_like_count),
                user_mentions = COALESCE(
                    extensions.mergeArrays(EXCLUDED.user_mentions,
                    topical."post_reaction".user_mentions), ARRAY[]::text[]);
            '''
        return insert_sql

    @staticmethod
    def post_insertsql(values_str: str, record_type):
        """Insert SQL for post values
        Note COALESCE:
        - coalesce will return the first value that is not Null
        - NULLIF(value1, value2) returns null if value1 and value2 match,
            otherwise returns value1
        - combining these allows to prevent overwriting of existing
            with default values
        - if existing values are also Null, a 3rd value can be added to
            specify the final default value (e.g. the one define in
            pgtable default)
        - "default" values in postgres table are only used on insert,
            never on update (upsert)
        """
        insert_sql = \
            f'''
            INSERT INTO topical."post" (
                {LBSNSql.DB_MAPPING.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id, post_guid)
            DO UPDATE SET
                post_latlng = COALESCE(
                    NULLIF(EXCLUDED.post_latlng,
                    '{HF.NULL_GEOM_HEX}'),
                    topical."post".post_latlng,
                    '{HF.NULL_GEOM_HEX}'),
                place_guid = COALESCE(EXCLUDED.place_guid,
                    topical."post".place_guid),
                city_guid = COALESCE(EXCLUDED.city_guid,
                    topical."post".city_guid),
                country_guid = COALESCE(EXCLUDED.country_guid,
                    topical."post".country_guid),
                post_geoaccuracy = COALESCE(NULLIF(EXCLUDED.post_geoaccuracy,'unknown'),
                    topical."post".post_geoaccuracy, 'unknown'),
                user_guid = COALESCE(EXCLUDED.user_guid,
                    topical."post".user_guid),
                post_create_date = COALESCE(EXCLUDED.post_create_date,
                    topical."post".post_create_date),
                post_publish_date = COALESCE(EXCLUDED.post_publish_date,
                    topical."post".post_publish_date),
                post_body = COALESCE(EXCLUDED.post_body,
                    topical."post".post_body),
                post_language = COALESCE(EXCLUDED.post_language,
                    topical."post".post_language),
                user_mentions = COALESCE(EXCLUDED.user_mentions,
                    topical."post".user_mentions),
                hashtags = COALESCE(extensions.mergeArrays(EXCLUDED.hashtags,
                    topical."post".hashtags), ARRAY[]::text[]),
                emoji = COALESCE(
                    extensions.mergeArrays(EXCLUDED.emoji,
                    topical."post".emoji), ARRAY[]::text[]),
                post_like_count = COALESCE(EXCLUDED.post_like_count,
                    topical."post".post_like_count),
                post_comment_count = COALESCE(EXCLUDED.post_comment_count,
                    topical."post".post_comment_count),
                post_views_count = COALESCE(EXCLUDED.post_views_count,
                    topical."post".post_views_count),
                post_title = COALESCE(EXCLUDED.post_title,
                    topical."post".post_title),
                post_thumbnail_url = COALESCE(EXCLUDED.post_thumbnail_url,
                    topical."post".post_thumbnail_url),
                post_url = COALESCE(EXCLUDED.post_url,
                    topical."post".post_url),
                post_type = COALESCE(NULLIF(EXCLUDED.post_type, 'text'),
                    topical."post".post_type, 'text'),
                post_filter = COALESCE(EXCLUDED.post_filter,
                    topical."post".post_filter),
                post_quote_count = COALESCE(EXCLUDED.post_quote_count,
                    topical."post".post_quote_count),
                post_share_count = COALESCE(EXCLUDED.post_share_count,
                    topical."post".post_share_count),
                input_source = COALESCE(EXCLUDED.input_source,
                    topical."post".input_source),
                post_content_license = COALESCE(
                    EXCLUDED.post_content_license,
                        topical."post".post_content_license);
            '''
        return insert_sql

    @staticmethod
    def user_insertsql(values_str: str, record_type):
        """SQL and value injection for lbsn.User"""
        insert_sql = \
            f'''
            INSERT INTO social."user" (
                {LBSNSql.DB_MAPPING.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id, user_guid)
            DO UPDATE SET
                user_name = COALESCE(EXCLUDED.user_name,
                    social."user".user_name),
                user_fullname = COALESCE(EXCLUDED.user_fullname,
                    social."user".user_fullname),
                follows = GREATEST(COALESCE(
                    EXCLUDED.follows, social."user".follows),
                    COALESCE(social."user".follows, EXCLUDED.follows)),
                followed = GREATEST(COALESCE(
                    EXCLUDED.followed, social."user".followed),
                    COALESCE(social."user".followed, EXCLUDED.followed)),
                group_count = GREATEST(COALESCE(
                    EXCLUDED.group_count, social."user".group_count),
                    COALESCE(social."user".group_count, EXCLUDED.group_count)),
                biography = COALESCE(EXCLUDED.biography,
                    social."user".biography),
                post_count = GREATEST(COALESCE(
                    EXCLUDED.post_count, "user".post_count),
                    COALESCE(social."user".post_count, EXCLUDED.post_count)),
                is_private = COALESCE(EXCLUDED.is_private,
                    social."user".is_private),
                url = COALESCE(EXCLUDED.url, social."user".url),
                is_available = COALESCE(EXCLUDED.is_available,
                    social."user".is_available),
                user_language = COALESCE(EXCLUDED.user_language,
                    social."user".user_language),
                user_location = COALESCE(EXCLUDED.user_location,
                    social."user".user_location),
                user_location_geom = COALESCE(EXCLUDED.user_location_geom,
                    social."user".user_location_geom),
                liked_count = GREATEST(COALESCE(
                    EXCLUDED.liked_count, social."user".liked_count),
                    COALESCE(social."user".liked_count, EXCLUDED.liked_count)),
                active_since = COALESCE(EXCLUDED.active_since,
                    social."user".active_since),
                profile_image_url = COALESCE(EXCLUDED.profile_image_url,
                    social."user".profile_image_url),
                user_timezone = COALESCE(EXCLUDED.user_timezone,
                    social."user".user_timezone),
                user_utc_offset = COALESCE(EXCLUDED.user_utc_offset,
                    social."user".user_utc_offset),
                user_groups_member = COALESCE(
                    extensions.mergeArrays(EXCLUDED.user_groups_member,
                    social."user".user_groups_member), ARRAY[]::text[]),
                user_groups_follows = COALESCE(
                    extensions.mergeArrays(EXCLUDED.user_groups_follows,
                    social."user".user_groups_follows), ARRAY[]::text[]);
            '''
        return insert_sql

    @staticmethod
    def usergroup_insertsql(values_str: str, record_type):
        """SQL and value injection for lbsn.UserGroup"""
        insert_sql = \
            f'''
            INSERT INTO social."user_groups" (
                {LBSNSql.DB_MAPPING.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id, usergroup_guid)
            DO UPDATE SET
                usergroup_name = COALESCE(EXCLUDED.usergroup_name,
                    social."user_groups".usergroup_name),
                usergroup_description = COALESCE(
                    EXCLUDED.usergroup_description,
                    social."user_groups".usergroup_description),
                member_count = GREATEST(COALESCE(
                    EXCLUDED.member_count, social."user_groups".member_count),
                    COALESCE(social."user_groups".member_count,
                    EXCLUDED.member_count)),
                usergroup_createdate = COALESCE(
                    EXCLUDED.usergroup_createdate,
                    social."user_groups".usergroup_createdate),
                user_owner = COALESCE(EXCLUDED.user_owner,
                    social."user_groups".user_owner);
            '''
        # No coalesce for user: in case user changes or
        # removes information, this should also be removed from the record
        return insert_sql

    @staticmethod
    def place_insertsql(values_str: str, record_type):
        """SQL and value injection for lbsn.Place"""
        insert_sql = \
            f'''
            INSERT INTO spatial."place" (
                {LBSNSql.DB_MAPPING.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id,place_guid)
            DO UPDATE SET
                name = COALESCE(EXCLUDED.name, spatial."place".name),
                name_alternatives = COALESCE((
                    SELECT array_remove(altNamesNewArray,spatial."place".name)
                    from extensions.mergeArrays(EXCLUDED.name_alternatives,
                    spatial."place".name_alternatives) AS altNamesNewArray),
                    ARRAY[]::text[]),
                geom_center = COALESCE(
                    NULLIF(EXCLUDED.geom_center,
                    '{HF.NULL_GEOM_HEX}'),
                    spatial."place".geom_center,
                    '{HF.NULL_GEOM_HEX}'),
                geom_area = COALESCE(EXCLUDED.geom_area,
                    spatial."place".geom_area),
                url = COALESCE(EXCLUDED.url, spatial."place".url),
                city_guid = COALESCE(EXCLUDED.city_guid,
                    spatial."place".city_guid),
                post_count = GREATEST(COALESCE(EXCLUDED.post_count,
                    spatial."place".post_count), COALESCE(
                        spatial."place".post_count, EXCLUDED.post_count)),
                place_description = COALESCE(
                    EXCLUDED.place_description, spatial."place".place_description),
                place_website = COALESCE(
                    EXCLUDED.place_website, spatial."place".place_website),
                place_phone = COALESCE(
                    EXCLUDED.place_phone, spatial."place".place_phone),
                address = COALESCE(
                    EXCLUDED.address, spatial."place".address),
                zip_code = COALESCE(
                    EXCLUDED.zip_code, spatial."place".zip_code),
                attributes = COALESCE(
                    EXCLUDED.attributes, spatial."place".attributes),
                checkin_count = COALESCE(
                    EXCLUDED.checkin_count, spatial."place".checkin_count),
                like_count = COALESCE(
                    EXCLUDED.like_count, spatial."place".like_count),
                parent_places = COALESCE(
                    extensions.mergeArrays(EXCLUDED.parent_places,
                    spatial."place".parent_places), ARRAY[]::text[]);
            '''
        return insert_sql

    @staticmethod
    def city_insertsql(values_str: str, record_type):
        """SQL and value injection for lbsn.City"""
        insert_sql = \
            f'''
            INSERT INTO spatial."city" (
                {LBSNSql.DB_MAPPING.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id,city_guid)
            DO UPDATE SET
                name = COALESCE(EXCLUDED.name, spatial."city".name),
                name_alternatives = COALESCE((
                    SELECT array_remove(altNamesNewArray,spatial."city".name)
                    from extensions.mergeArrays(EXCLUDED.name_alternatives,
                    spatial."city".name_alternatives) AS altNamesNewArray),
                    ARRAY[]::text[]),
                geom_center = COALESCE(
                    NULLIF(EXCLUDED.geom_center,
                    '{HF.NULL_GEOM_HEX}'),
                    spatial."city".geom_center,
                    '{HF.NULL_GEOM_HEX}'),
                geom_area = COALESCE(EXCLUDED.geom_area,
                    spatial."city".geom_area),
                url = COALESCE(EXCLUDED.url, spatial."city".url),
                country_guid = COALESCE(EXCLUDED.country_guid,
                    spatial."city".country_guid),
                sub_type = COALESCE(EXCLUDED.sub_type, spatial."city".sub_type);
            '''
        return insert_sql

    @staticmethod
    def country_insertsql(values_str: str, record_type):
        """SQL and value injection for lbsn.Country"""
        insert_sql = \
            f'''
            INSERT INTO spatial."country" (
                {LBSNSql.DB_MAPPING.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id,country_guid)
            DO UPDATE SET
                name = COALESCE(EXCLUDED.name, spatial."country".name),
                name_alternatives = COALESCE((
                    SELECT array_remove(altNamesNewArray,spatial."country".name)
                    from extensions.mergeArrays(EXCLUDED.name_alternatives,
                    spatial."country".name_alternatives) AS altNamesNewArray),
                    ARRAY[]::text[]),
                geom_center = COALESCE(
                    NULLIF(EXCLUDED.geom_center,
                    '{HF.NULL_GEOM_HEX}'),
                    spatial."country".geom_center,
                    '{HF.NULL_GEOM_HEX}'),
                geom_area = COALESCE(EXCLUDED.geom_area,
                    spatial."country".geom_area),
                url = COALESCE(EXCLUDED.url, spatial."country".url);
            '''
        # Array merge of alternatives:
        # Arrays cannot be null, therefore COALESCE(
        # [if array not null],[otherwise create empty array])
        # We don't want the english name to appear in alternatives,
        # therefore: array_remove(altNamesNewArray,"country".name)
        # Finally, merge New Entries with existing ones (distinct):
        # extensions.mergeArrays([new],[old]) uses custom mergeArrays
        # function (see function definitions)
        return insert_sql

    @staticmethod
    def event_insertsql(values_str: str, record_type):
        """Insert SQL for event values
        """
        insert_sql = \
            f'''
            INSERT INTO temporal."event" (
                {LBSNSql.DB_MAPPING.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id, event_guid)
            DO UPDATE SET
                name = COALESCE(EXCLUDED.name,
                    temporal."event".name),
                event_latlng = COALESCE(
                    NULLIF(EXCLUDED.event_latlng,
                    '{HF.NULL_GEOM_HEX}'),
                    temporal."event".event_latlng,
                    '{HF.NULL_GEOM_HEX}'),
                event_area = COALESCE(EXCLUDED.event_area,
                    temporal."event".event_area),
                event_website = COALESCE(EXCLUDED.event_website,
                    temporal."event".event_website),
                event_date = COALESCE(EXCLUDED.event_date,
                    temporal."event".event_date),
                event_date_start = COALESCE(EXCLUDED.event_date_start,
                    temporal."event".event_date_start),
                event_date_end = COALESCE(EXCLUDED.event_date_end,
                    temporal."event".event_date_end),
                duration = COALESCE(EXCLUDED.duration,
                    temporal."event".duration),
                place_guid = COALESCE(EXCLUDED.place_guid,
                    temporal."event".place_guid),
                city_guid = COALESCE(EXCLUDED.city_guid,
                    temporal."event".city_guid),
                country_guid = COALESCE(EXCLUDED.country_guid,
                    temporal."event".country_guid),
                user_guid = COALESCE(EXCLUDED.user_guid,
                    temporal."event".user_guid),
                event_description = COALESCE(EXCLUDED.event_description,
                    temporal."event".event_description),
                event_type = COALESCE(EXCLUDED.event_type,
                    temporal."event".event_type),
                event_share_count = COALESCE(EXCLUDED.event_share_count,
                    temporal."event".event_share_count),
                event_like_count = COALESCE(EXCLUDED.event_like_count,
                    temporal."event".event_like_count),
                event_comment_count = COALESCE(EXCLUDED.event_comment_count,
                    temporal."event".event_comment_count),
                event_views_count = COALESCE(EXCLUDED.event_views_count,
                    temporal."event".event_views_count),
                event_engage_count = COALESCE(EXCLUDED.event_engage_count,
                    temporal."event".event_engage_count);
            '''
        return insert_sql