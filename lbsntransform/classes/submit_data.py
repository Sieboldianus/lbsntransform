# -*- coding: utf-8 -*-

"""
Module for storing common Proto LBSN Structure to PG DB.
"""

# pylint: disable=no-member

import logging
import os
import sys
import traceback
from glob import glob
from sys import exit
import psycopg2

from lbsnstructure.lbsnstructure_pb2 import (CompositeKey, RelationshipKey,
                                             lbsnCity, lbsnCountry, lbsnPlace,
                                             lbsnPost, lbsnPostReaction,
                                             lbsnRelationship, lbsnUser,
                                             lbsnUserGroup)
from psycopg2 import sql

from .helper_functions import HelperFunctions, LBSNRecordDicts
from .shared_structure_proto_lbsndb import ProtoLBSNMapping
from .store_csv import LBSNcsv

# for debugging only:
from google.protobuf import text_format
from google.protobuf.timestamp_pb2 import Timestamp

# due to different protocol buffers implementations, import both possible types
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
try:
    from google.protobuf.pyext._message import RepeatedCompositeContainer
except ImportError:
    pass


class LBSNTransfer():
    def __init__(self, db_cursor=None,
                 db_connection=None,
                 commit_volume=10000,
                 disable_reaction_post_ref=0,
                 store_csv=None,
                 SUPPRESS_LINEBREAKS=True):
        self.db_cursor = db_cursor
        self.db_connection = db_connection
        if not self.db_cursor:
            print("CSV Output Mode.")
        self.count_entries_commit = 0
        self.count_entries_store = 0
        self.count_affected = 0
        self.commit_volume = commit_volume
        self.store_volume = 500000
        self.count_glob = 0
        self.null_island_count = 0
        self.disable_reaction_post_ref = disable_reaction_post_ref
        self.log = logging.getLogger('__main__')
        self.batched_records = {
            lbsnCountry.DESCRIPTOR.name: list(),
            lbsnCity.DESCRIPTOR.name: list(),
            lbsnPlace.DESCRIPTOR.name: list(),
            lbsnUser.DESCRIPTOR.name: list(),
            lbsnUserGroup.DESCRIPTOR.name: list(),
            lbsnPost.DESCRIPTOR.name: list(),
            lbsnPostReaction.DESCRIPTOR.name: list(),
            lbsnRelationship.DESCRIPTOR.name: list()}

        self.count_round = 0
        # Records are batched and submitted in
        # one insert with x number of records
        self.batch_db_volume = 100
        self.store_csv = store_csv
        self.headers_written = set()
        self.db_mapping = ProtoLBSNMapping()
        # self.CSVsuppressLinebreaks = CSVsuppressLinebreaks

        if self.store_csv:
            self.csv_output = LBSNcsv(SUPPRESS_LINEBREAKS)

    def commit_changes(self):
        """Commit Changes to DB"""
        if self.db_cursor:
            self.db_connection.commit()  #
            self.count_entries_commit = 0

    def store_changes(self):
        """Write changes to CSV"""
        if self.store_csv:
            self.csv_output.clean_csv_batches(
                self.batched_records)
            self.count_entries_store = 0

    def store_origin(self, origin_id, name):
        insert_sql = \
            f'''
            INSERT INTO data."origin" (
                origin_id, name)
            VALUES ({origin_id},'{name}')
            ON CONFLICT (origin_id)
            DO NOTHING
            '''
        self.db_cursor.execute(insert_sql)

    def store_lbsn_record_dicts(self, lbsn_record_dicts):
        """Main loop for storing lbsn records to CSV or DB

        Arguments:
            field_mapping {field mapping class} -- Import Field mapping class
            with attached data

        order is important here, as PostGres will reject any
        records where Foreign Keys are violated
        therefore, records are processed starting from lowest
        granularity. Order is stored in allDicts()
        """

        self.count_round += 1
        # self.headersWritten.clear()
        r_cnt = 0
        self.count_affected = 0
        for records_dict in lbsn_record_dicts.all_dicts:
            type_name = records_dict[1]
            for record in records_dict[0].values():
                r_cnt += 1
                print(f'Storing {r_cnt} of {lbsn_record_dicts.count_glob} '
                      f'output records ({type_name})..', end='\r')
                self.prepare_lbsn_record(record, type_name)
                self.count_glob += 1  # self.dbCursor.rowcount
                self.count_entries_commit += 1  # self.dbCursor.rowcount
                self.count_entries_store += 1
                if self.db_cursor and (self.count_glob == 100 or
                                       self.count_entries_commit >
                                       self.commit_volume):
                    self.commit_changes()
                if self.store_csv and (self.count_entries_store >
                                       self.store_volume):
                    self.store_changes()
        # submit remaining rest
        self.submit_all_batches()
        # self.count_affected += x # monitoring
        print(f'\nRound {self.count_round:03d}: '
              f'Updated/Inserted {self.count_glob} records.')

    def prepare_lbsn_record(self, record, record_type):
        # clean duplicates in repeated Fields and Sort List
        self.sort_clean_proto_repeated_field(record)
        # store cleaned ProtoBuf records
        self.batched_records[record_type].append(record)
        for batch_list in self.batched_records.values():
            # if any dict contains more values than self.batchDBVolume,
            # submit/store all
            if len(batch_list) >= self.batch_db_volume:
                self.submit_all_batches()

    def submit_all_batches(self):
        for record_type, batch_list in self.batched_records.items():
            if batch_list:
                # if self.storeCSV and not record_type in self.headersWritten:
                #    self.writeCSVHeader(record_type)
                #    self.headersWritten.add(record_type)
                self.submit_lbsn_records(record_type)
                # self.funcSubmitSelector(record_type)
                batch_list.clear()

    def prepare_records(self, record_type):
        prepared_records = []
        for record in self.batched_records[record_type]:
            prepared_record = self.db_mapping.func_prepare_selector(record)
            if prepared_record:
                prepared_records.append(prepared_record)
        return prepared_records

    def submit_lbsn_records(self, record_type):
        prepared_records = self.prepare_records(record_type)
        if self.store_csv:
            self.csv_output.store_append_batch_to_csv(
                self.batched_records[record_type],
                self.count_round, record_type)
        if self.db_cursor:
            values_str = ','.join(
                [self.prepare_sqlescaped_values(record) for
                 record in prepared_records])
            insert_sql = self.insert_sql_selector(values_str, record_type)
            self.submitBatch(insert_sql)

    def insert_sql_selector(self, values_str, record_type):
        """ Select function to prepare SQL insert.

        Attributes:
            record_type     type of record
            values_str      values to be inserted
        """
        dict_switcher = {
            lbsnCountry().DESCRIPTOR.name: self.country_insertsql,
            lbsnCity().DESCRIPTOR.name: self.city_insertsql,
            lbsnPlace().DESCRIPTOR.name: self.place_insertsql,
            lbsnUser().DESCRIPTOR.name: self.user_insertsql,
            lbsnUserGroup().DESCRIPTOR.name: self.usergroup_insertsql,
            lbsnPost().DESCRIPTOR.name: self.post_insertsql,
            lbsnPostReaction().DESCRIPTOR.name: self.postreaction_insertsql,
        }
        prepare_function = dict_switcher.get(record_type)
        return prepare_function(values_str, record_type)

    def postreaction_insertsql(self, values_str, record_type):
        insert_sql = \
            f'''
            INSERT INTO data."post_reaction" (
                {self.db_mapping.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id, reaction_guid)
            DO UPDATE SET
                reaction_latlng = COALESCE(
                    NULLIF(EXCLUDED.reaction_latlng,'0101000020E610000000000000000000000000000000000000'),
                    data."post_reaction".reaction_latlng,
                    '0101000020E610000000000000000000000000000000000000'),
                user_guid = COALESCE(EXCLUDED.user_guid,
                    data."post_reaction".user_guid),
                referencedPost_guid = COALESCE(EXCLUDED.referencedPost_guid,
                    data."post_reaction".referencedPost_guid),
                referencedPostreaction_guid = COALESCE(
                    EXCLUDED.referencedPostreaction_guid,
                    data."post_reaction".referencedPostreaction_guid),
                reaction_type = COALESCE(NULLIF(EXCLUDED.reaction_type, 'unknown'),
                    data."post_reaction".reaction_type, 'unknown'),
                reaction_date = COALESCE(EXCLUDED.reaction_date,
                    data."post_reaction".reaction_date),
                reaction_content = COALESCE(EXCLUDED.reaction_content,
                    data."post_reaction".reaction_content),
                reaction_like_count = COALESCE(EXCLUDED.reaction_like_count,
                    data."post_reaction".reaction_like_count),
                user_mentions = COALESCE(
                    extensions.mergeArrays(EXCLUDED.user_mentions,
                    data."post_reaction".user_mentions), ARRAY[]::text[]);
            '''
        return insert_sql

    def post_insertsql(self, values_str, record_type):
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
            INSERT INTO data."post" (
                {self.db_mapping.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id, post_guid)
            DO UPDATE SET
                post_latlng = COALESCE(
                    NULLIF(EXCLUDED.post_latlng,'0101000020E610000000000000000000000000000000000000'),
                    data."post".post_latlng, '0101000020E610000000000000000000000000000000000000'),
                place_guid = COALESCE(EXCLUDED.place_guid,
                    data."post".place_guid),
                city_guid = COALESCE(EXCLUDED.city_guid,
                    data."post".city_guid),
                country_guid = COALESCE(EXCLUDED.country_guid,
                    data."post".country_guid),
                post_geoaccuracy = COALESCE(NULLIF(EXCLUDED.post_geoaccuracy,'unknown'),
                    data."post".post_geoaccuracy, 'unknown'),
                user_guid = COALESCE(EXCLUDED.user_guid,
                    data."post".user_guid),
                post_create_date = COALESCE(EXCLUDED.post_create_date,
                    data."post".post_create_date),
                post_publish_date = COALESCE(EXCLUDED.post_publish_date,
                    data."post".post_publish_date),
                post_body = COALESCE(EXCLUDED.post_body,
                    data."post".post_body),
                post_language = COALESCE(EXCLUDED.post_language,
                    data."post".post_language),
                user_mentions = COALESCE(EXCLUDED.user_mentions,
                    data."post".user_mentions),
                hashtags = COALESCE(extensions.mergeArrays(EXCLUDED.hashtags,
                    data."post".hashtags), ARRAY[]::text[]),
                emoji = COALESCE(
                    extensions.mergeArrays(EXCLUDED.emoji,
                    data."post".emoji), ARRAY[]::text[]),
                post_like_count = COALESCE(EXCLUDED.post_like_count,
                    data."post".post_like_count),
                post_comment_count = COALESCE(EXCLUDED.post_comment_count,
                    data."post".post_comment_count),
                post_views_count = COALESCE(EXCLUDED.post_views_count,
                    data."post".post_views_count),
                post_title = COALESCE(EXCLUDED.post_title,
                    data."post".post_title),
                post_thumbnail_url = COALESCE(EXCLUDED.post_thumbnail_url,
                    data."post".post_thumbnail_url),
                post_url = COALESCE(EXCLUDED.post_url,
                    data."post".post_url),
                post_type = COALESCE(NULLIF(EXCLUDED.post_type, 'text'),
                    data."post".post_type, 'text'),
                post_filter = COALESCE(EXCLUDED.post_filter,
                    data."post".post_filter),
                post_quote_count = COALESCE(EXCLUDED.post_quote_count,
                    data."post".post_quote_count),
                post_share_count = COALESCE(EXCLUDED.post_share_count,
                    data."post".post_share_count),
                input_source = COALESCE(EXCLUDED.input_source,
                    data."post".input_source),
                post_content_license = COALESCE(
                    EXCLUDED.post_content_license,
                        data."post".post_content_license);
            '''
        return insert_sql

    def user_insertsql(self, values_str, record_type):
        insert_sql = \
            f'''
            INSERT INTO data."user" (
                {self.db_mapping.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id, user_guid)
            DO UPDATE SET
                user_name = COALESCE(EXCLUDED.user_name,
                    data."user".user_name),
                user_fullname = COALESCE(EXCLUDED.user_fullname,
                    data."user".user_fullname),
                follows = GREATEST(COALESCE(
                    EXCLUDED.follows, data."user".follows),
                    COALESCE(data."user".follows, EXCLUDED.follows)),
                followed = GREATEST(COALESCE(
                    EXCLUDED.followed, data."user".followed),
                    COALESCE(data."user".followed, EXCLUDED.followed)),
                group_count = GREATEST(COALESCE(
                    EXCLUDED.group_count, data."user".group_count),
                    COALESCE(data."user".group_count, EXCLUDED.group_count)),
                biography = COALESCE(EXCLUDED.biography,
                    data."user".biography),
                post_count = GREATEST(COALESCE(
                    EXCLUDED.post_count, "user".post_count),
                    COALESCE(data."user".post_count, EXCLUDED.post_count)),
                is_private = COALESCE(EXCLUDED.is_private,
                    data."user".is_private),
                url = COALESCE(EXCLUDED.url, data."user".url),
                is_available = COALESCE(EXCLUDED.is_available,
                    data."user".is_available),
                user_language = COALESCE(EXCLUDED.user_language,
                    data."user".user_language),
                user_location = COALESCE(EXCLUDED.user_location,
                    data."user".user_location),
                user_location_geom = COALESCE(EXCLUDED.user_location_geom,
                    data."user".user_location_geom),
                liked_count = GREATEST(COALESCE(
                    EXCLUDED.liked_count, data."user".liked_count),
                    COALESCE(data."user".liked_count, EXCLUDED.liked_count)),
                active_since = COALESCE(EXCLUDED.active_since,
                    data."user".active_since),
                profile_image_url = COALESCE(EXCLUDED.profile_image_url,
                    data."user".profile_image_url),
                user_timezone = COALESCE(EXCLUDED.user_timezone,
                    data."user".user_timezone),
                user_utc_offset = COALESCE(EXCLUDED.user_utc_offset,
                    data."user".user_utc_offset),
                user_groups_member = COALESCE(
                    extensions.mergeArrays(EXCLUDED.user_groups_member,
                    data."user".user_groups_member), ARRAY[]::text[]),
                user_groups_follows = COALESCE(
                    extensions.mergeArrays(EXCLUDED.user_groups_follows,
                    data."user".user_groups_follows), ARRAY[]::text[]);
            '''
        return insert_sql

    def usergroup_insertsql(self, values_str, record_type):
        insert_sql = \
            f'''
            INSERT INTO data."user_groups" (
                {self.db_mapping.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id, usergroup_guid)
            DO UPDATE SET
                usergroup_name = COALESCE(EXCLUDED.usergroup_name,
                    data."user_groups".usergroup_name),
                usergroup_description = COALESCE(
                    EXCLUDED.usergroup_description,
                    data."user_groups".usergroup_description),
                member_count = GREATEST(COALESCE(
                    EXCLUDED.member_count, data."user_groups".member_count),
                    COALESCE(data."user_groups".member_count,
                    EXCLUDED.member_count)),
                usergroup_createdate = COALESCE(
                    EXCLUDED.usergroup_createdate,
                    data."user_groups".usergroup_createdate),
                user_owner = COALESCE(EXCLUDED.user_owner,
                    data."user_groups".user_owner);
            '''
        # No coalesce for user: in case user changes or
        # removes information, this should also be removed from the record
        return insert_sql

    def place_insertsql(self, values_str, record_type):
        insert_sql = \
            f'''
            INSERT INTO data."place" (
                {self.db_mapping.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id,place_guid)
            DO UPDATE SET
                name = COALESCE(EXCLUDED.name, data."place".name),
                name_alternatives = COALESCE((
                    SELECT array_remove(altNamesNewArray,data."place".name)
                    from extensions.mergeArrays(EXCLUDED.name_alternatives,
                    data."place".name_alternatives) AS altNamesNewArray),
                    ARRAY[]::text[]),
                geom_center = COALESCE(EXCLUDED.geom_center,
                    data."place".geom_center),
                geom_area = COALESCE(EXCLUDED.geom_area,
                    data."place".geom_area),
                url = COALESCE(EXCLUDED.url, data."place".url),
                city_guid = COALESCE(EXCLUDED.city_guid,
                    data."place".city_guid),
                post_count = GREATEST(COALESCE(EXCLUDED.post_count,
                    data."place".post_count), COALESCE(
                        data."place".post_count, EXCLUDED.post_count));
            '''
        return insert_sql

    def city_insertsql(self, values_str, record_type):
        insert_sql = \
            f'''
            INSERT INTO data."city" (
                {self.db_mapping.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id,city_guid)
            DO UPDATE SET
                name = COALESCE(EXCLUDED.name, data."city".name),
                name_alternatives = COALESCE((
                    SELECT array_remove(altNamesNewArray,data."city".name)
                    from extensions.mergeArrays(EXCLUDED.name_alternatives,
                    data."city".name_alternatives) AS altNamesNewArray),
                    ARRAY[]::text[]),
                geom_center = COALESCE(EXCLUDED.geom_center,
                    data."city".geom_center),
                geom_area = COALESCE(EXCLUDED.geom_area,
                    data."city".geom_area),
                url = COALESCE(EXCLUDED.url, data."city".url),
                country_guid = COALESCE(EXCLUDED.country_guid,
                    data."city".country_guid),
                sub_type = COALESCE(EXCLUDED.sub_type, data."city".sub_type);
            '''
        return insert_sql

    def country_insertsql(self, values_str, record_type):
        insert_sql = \
            f'''
            INSERT INTO data."country" (
                {self.db_mapping.get_header_for_type(record_type)})
            VALUES {values_str}
            ON CONFLICT (origin_id,country_guid)
            DO UPDATE SET
                name = COALESCE(EXCLUDED.name, data."country".name),
                name_alternatives = COALESCE((
                    SELECT array_remove(altNamesNewArray,data."country".name)
                    from extensions.mergeArrays(EXCLUDED.name_alternatives,
                    data."country".name_alternatives) AS altNamesNewArray),
                    ARRAY[]::text[]),
                geom_center = COALESCE(EXCLUDED.geom_center,
                    data."country".geom_center),
                geom_area = COALESCE(EXCLUDED.geom_area,
                    data."country".geom_area),
                url = COALESCE(EXCLUDED.url, data."country".url);
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

    def submitLbsnRelationships(self):
        """submit relationships of different types

        record[1] is the PostgresQL formatted list of values,
        record[0] is the type of relationship that determines
            the table selection
        """
        selectFriends = [relationship[1] for relationship in
                         self.batched_records[lbsnRelationship(
                         ).DESCRIPTOR.name] if relationship[0] == "isfriend"]
        if selectFriends:
            if self.store_csv:
                self.csv_output.store_append_batch_to_csv(
                    selectFriends, self.count_round, '_user_friends_user')
            if self.db_cursor:
                args_isFriend = ','.join(selectFriends)
                insert_sql = \
                    f'''
                    INSERT INTO relations."_user_friends_user" (
                        {self.typeNamesHeaderDict["_user_friends_user"]})
                    VALUES {args_isFriend}
                    ON CONFLICT (origin_id, user_guid, friend_guid)
                    DO NOTHING
                    '''
                self.submitBatch(insert_sql)
        selectConnected = [relationship[1] for relationship in
                           self.batched_records[lbsnRelationship(
                           ).DESCRIPTOR.name] if
                           relationship[0] == "isconnected"]
        if selectConnected:
            if self.store_csv:
                self.csv_output.store_append_batch_to_csv(
                    selectConnected, self.count_round, '_user_connectsto_user')
            if self.db_cursor:
                args_isConnected = ','.join(selectConnected)
                insert_sql = \
                    f'''
                        INSERT INTO relations."_user_connectsto_user" (
                            {self.typeNamesHeaderDict["_user_connectsto_user"]})
                        VALUES {args_isConnected}
                        ON CONFLICT (origin_id, user_guid,
                            connectedto_user_guid)
                        DO NOTHING
                    '''
                self.submitBatch(insert_sql)
        selectUserGroupMember = [relationship[1] for relationship in
                                 self.batched_records[lbsnRelationship(
                                 ).DESCRIPTOR.name] if
                                 relationship[0] == "ingroup"]
        if selectUserGroupMember:
            if self.store_csv:
                self.csv_output.store_append_batch_to_csv(
                    selectUserGroupMember, self.count_round,
                    '_user_memberof_group')
            if self.db_cursor:
                args_isInGroup = ','.join(selectUserGroupMember)
                insert_sql = \
                    f'''
                    INSERT INTO relations."_user_memberof_group" (
                        {self.typeNamesHeaderDict["_user_memberof_group"]})
                    VALUES {args_isInGroup}
                    ON CONFLICT (origin_id, user_guid, group_guid)
                    DO NOTHING
                    '''
                self.submitBatch(insert_sql)
        selectUserGroupMember = [relationship[1] for relationship in
                                 self.batched_records[lbsnRelationship(
                                 ).DESCRIPTOR.name] if
                                 relationship[0] == "followsgroup"]
        if selectUserGroupMember:
            if self.store_csv:
                self.csv_output.store_append_batch_to_csv(
                    selectUserGroupMember, self.count_round,
                    '_user_follows_group')
            if self.db_cursor:
                args_isInGroup = ','.join(selectUserGroupMember)
                insert_sql = \
                    f'''
                    INSERT INTO relations."_user_follows_group" (
                        {self.typeNamesHeaderDict["_user_follows_group"]})
                    VALUES {args_isInGroup}
                    ON CONFLICT (origin_id, user_guid, group_guid)
                    DO NOTHING
                    '''
                self.submitBatch(insert_sql)
        selectUserMentions = [relationship[1] for relationship in
                              self.batched_records[lbsnRelationship(
                              ).DESCRIPTOR.name] if
                              relationship[0] == "mentions_user"]
        if selectUserMentions:
            if self.store_csv:
                self.csv_output.store_append_batch_to_csv(
                    selectUserMentions, self.count_round,
                    '_user_mentions_user')
            if self.db_cursor:
                args_isInGroup = ','.join(selectUserMentions)
                insert_sql = \
                    f'''
                    INSERT INTO relations."_user_mentions_user" (
                        {self.typeNamesHeaderDict["_user_mentions_user"]})
                    VALUES {args_isInGroup}
                    ON CONFLICT (origin_id, user_guid, mentioneduser_guid)
                    DO NOTHING
                    '''
                self.submitBatch(insert_sql)

    def submitBatch(self, insert_sql):
        """Submit Batch to PG DB.

        Needs testing: is using Savepoint for each insert slower
        than rolling back entire commit?
        for performance, see https://stackoverflow.com/questions/
            12206600/how-to-speed-up-insertion-performance-in-postgresql
        or this: https://stackoverflow.com/questions/8134602/
        psycopg2-insert-multiple-rows-with-one-query
        """
        self.db_cursor.execute("SAVEPOINT submit_recordBatch")
        tsuccessful = False
        while not tsuccessful:
            try:
                self.db_cursor.execute(insert_sql)
            except psycopg2.IntegrityError as e:
                if '(post_language)' in e.diag.message_detail or \
                        '(user_language)' in e.diag.message_detail:
                    # If language does not exist, we'll trust Twitter
                    # and add this to our language list
                    missingLanguage = e.diag.message_detail.partition(
                        "language)=(")[2].partition(") is not present")[0]
                    print(
                        f'TransactionIntegrityError, inserting language "'
                        f'{missingLanguage}" first..               ')
                    self.db_cursor.execute(
                        "ROLLBACK TO SAVEPOINT submit_recordBatch")
                    insert_language_sql = '''
                           INSERT INTO data."language"
                            (language_short,language_name,language_name_de)
                           VALUES (%s,NULL,NULL);
                           '''
                    self.db_cursor.execute(
                        insert_language_sql, (missingLanguage,))
                else:
                    sys.exit(f'{e}')
            except psycopg2.DataError as e:
                sys.exit(f'{e}\nINSERT SQL WAS: {insert_sql}')
            except ValueError as e:
                self.log.warning(f'{e}')
                input("Press Enter to continue... (entry will be skipped)")
                self.log.warning(f'{insert_sql}')
                input("args:... ")
                # self.log.warning(f'{args_str}')
                self.db_cursor.execute(
                    "ROLLBACK TO SAVEPOINT submit_recordBatch")
                tsuccessful = True
            except psycopg2.ProgrammingError as e:
                sys.exit(f'{e}\nINSERT SQL WAS: {insert_sql}')
            else:
                # self.count_affected += self.dbCursor.rowcount # monitoring
                self.db_cursor.execute("RELEASE SAVEPOINT submit_recordBatch")
                tsuccessful = True

    def prepare_sqlescaped_values(self, *args):
        # dynamically construct sql value injection
        # e.g. record_sql = '''(%s,%s,%s,%s,%s,%s,%s)'''
        record_sql = f'''{','.join('%s' for x in range(0, len(args)))}'''
        # inject values
        preparedSQLRecord = self.db_cursor.mogrify(record_sql, tuple(args))
        # mogrify returns a byte object,
        # we decode it so it can be used as a string again
        preparedSQLRecord = preparedSQLRecord.decode()
        return preparedSQLRecord

    def sort_clean_proto_repeated_field(self, record):
        """Remove duplicate values in repeated field, sort alphabetically

        ProtocolBuffers has no unique list field type. This function will
        remove duplicates, which is needed for unique compare.

        There is a 'bug' in Python implementation of ProtocolBuffers:
        - depending on the implementation type in use, it is possible
        to spot either 'RepeatedCompositeFieldContainer'
            or 'RepeatedCompositeContainer'
        - solution here: import and compare to both types
        - this is not ideal, since both types are internal to PB and
            subject to change
        - see [proto-bug](https://github.com/protocolbuffers/
            protobuf/issues/3870)
        """
        for descriptor in record.DESCRIPTOR.fields:
            if descriptor.label == descriptor.LABEL_REPEATED:
                x = getattr(record, descriptor.name)
                if x and not (isinstance(x, RepeatedCompositeFieldContainer) or
                              isinstance(x, RepeatedCompositeContainer)):
                    xCleaned = set(x)
                    xSorted = sorted(xCleaned)
                    # Complete clear of repeated field
                    for _ in range(0, len(x)):
                        x.pop()
                    # add sorted list
                    x.extend(xSorted)

    def finalize(self):
        """ Final procedure calls:
            - clean and merge csv batches
        """
        if self.store_csv:
            self.csv_output.clean_csv_batches(self.batched_records)
