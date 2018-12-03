# -*- coding: utf-8 -*-

import psycopg2
from .helper_functions import HelperFunctions
from .helper_functions import LBSNRecordDicts
from .store_csv import LBSNcsv
from .shared_structure_proto_lbsndb import ProtoLBSM_db_Mapping
#from lbsn2structure import *
from lbsnstructure.lbsnstructure_pb2 import *
from google.protobuf.timestamp_pb2 import Timestamp
import logging
from sys import exit
import traceback
import os
import sys
# for debugging only:
from google.protobuf import text_format
import re
from psycopg2 import sql
import csv
from glob import glob
import shutil

from google.protobuf.internal import encoder
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
import base64

class LBSNTransfer():
    def __init__(self, dbCursor = None,
                 dbConnection = None,
                 commit_volume = 10000,
                 disableReactionPostReferencing = 0, storeCSV = None, SUPPRESS_LINEBREAKS = True):
        self.dbCursor = dbCursor
        self.dbConnection = dbConnection
        if not self.dbCursor:
            print("CSV Output Mode.")
        self.count_entries_commit = 0
        self.count_entries_store = 0
        self.count_affected = 0
        self.commit_volume = commit_volume
        self.store_volume = 500000
        self.count_glob = 0
        self.null_island_count = 0
        self.disableReactionPostReferencing = disableReactionPostReferencing
        self.log = logging.getLogger('__main__')
        self.batchedRecords = {lbsnCountry.DESCRIPTOR.name: list(),
                         lbsnCity.DESCRIPTOR.name: list(),
                         lbsnPlace.DESCRIPTOR.name: list(),
                         lbsnUser.DESCRIPTOR.name: list(),
                         lbsnUserGroup.DESCRIPTOR.name: list(),
                         lbsnPost.DESCRIPTOR.name: list(),
                         lbsnPostReaction.DESCRIPTOR.name: list(),
                         lbsnRelationship.DESCRIPTOR.name: list()}

        self.countRound = 0
        self.batchDBVolume = 100 # Records are batched and submitted in one insert with x number of records
        self.storeCSV = storeCSV
        self.headersWritten = set()
        self.db_mapping = ProtoLBSM_db_Mapping()
        #self.CSVsuppressLinebreaks = CSVsuppressLinebreaks

        if self.storeCSV:
            self.csv_output = LBSNcsv(SUPPRESS_LINEBREAKS)

    def commitChanges(self):
        if self.dbCursor:
            self.dbConnection.commit() # commit changes to db
            self.count_entries_commit = 0

    def storeChanges(self):
        if self.storeCSV:
            self.csv_output.clean_csv_batches(self.batchedRecords)
            self.count_entries_store = 0

    def storeLbsnRecordDicts(self, fieldMappingTwitter):
        # order is important here, as PostGres will reject any records where Foreign Keys are violated
        # therefore, records are processed starting from lowest granularity. Order is stored in allDicts()
        self.countRound += 1
        #self.headersWritten.clear()
        recordDicts = fieldMappingTwitter.lbsnRecords
        x = 0
        self.count_affected = 0
        for recordsDict in recordDicts.allDicts:
            type_name = recordsDict[1]
            for record_pkey, record in recordsDict[0].items():
                x += 1
                print(f'Storing {x} of {recordDicts.CountGlob} output records ({type_name})..', end='\r')
                self.prepareLbsnRecord(record,type_name)
                self.count_glob +=  1 #self.dbCursor.rowcount
                self.count_entries_commit +=  1 #self.dbCursor.rowcount
                self.count_entries_store += 1
                if self.dbCursor and (self.count_glob == 100 or self.count_entries_commit > self.commit_volume):
                    self.commitChanges()
                if self.storeCSV and (self.count_entries_store > self.store_volume):
                    self.storeChanges()
        # submit remaining rest
        self.submitAllBatches()
        #self.count_affected += x # monitoring
        print(f'\nRound {self.countRound:03d}: Updated/Inserted {self.count_glob} records.')

    def prepareLbsnRecord(self, record, record_type):
        # clean duplicates in repeated Fields and Sort List
        self.sortCleanProtoRepeatedField(record)
        # store cleaned ProtoBuf records
        self.batchedRecords[record_type].append(record)
        for listType, batchList in self.batchedRecords.items():
            # if any dict contains more values than self.batchDBVolume, submit/store all
            if len(batchList) >= self.batchDBVolume:
                self.submitAllBatches()



    def submitAllBatches(self):
        for recordType, batchList in self.batchedRecords.items():
            if batchList:
                #if self.storeCSV and not recordType in self.headersWritten:
                #    self.writeCSVHeader(recordType)
                #    self.headersWritten.add(recordType)
                self.submitLbsnRecords(recordType)
                #self.funcSubmitSelector(recordType)
                batchList.clear()

    def prepareRecords(self, recordType):
        preparedRecords = []
        for record in self.batchedRecords[recordType]:
            preparedRecord = self.db_mapping.func_prepare_selector(record)
            if preparedRecord:
                preparedRecords.append(preparedRecord)
        return preparedRecords

    def submitLbsnRecords(self, recordType):
        preparedRecords = self.prepareRecords(recordType)
        if self.storeCSV:
            self.csv_output.store_append_batch_to_csv(self.batchedRecords[recordType], self.countRound, recordType)
        if self.dbCursor:
            values_str = ','.join([self.prepareSQLEscapedValues(record) for record in preparedRecords])
            if recordType == lbsnCountry().DESCRIPTOR.name:
                insert_sql = f'''
                            INSERT INTO data."country" ({self.db_mapping.get_header_for_type(recordType)})
                            VALUES {values_str}
                            ON CONFLICT (origin_id,country_guid)
                            DO UPDATE SET
                                name = COALESCE(EXCLUDED.name, data."country".name),
                                name_alternatives = COALESCE((SELECT array_remove(altNamesNewArray,data."country".name) from extensions.mergeArrays(EXCLUDED.name_alternatives, data."country".name_alternatives) AS altNamesNewArray), ARRAY[]::text[]),
                                geom_center = COALESCE(EXCLUDED.geom_center, data."country".geom_center),
                                geom_area = COALESCE(EXCLUDED.geom_area, data."country".geom_area),
                                url = COALESCE(EXCLUDED.url, data."country".url);
                            '''
                            # Array merge of alternatives:
                            # Arrays cannot be null, therefore COALESCE([if array not null],[otherwise create empty array])
                            # We don't want the english name to appear in alternatives, therefore: array_remove(altNamesNewArray,"country".name)
                            # Finally, merge New Entries with existing ones (distinct): extensions.mergeArrays([new],[old]) uses custom mergeArrays function (see function definitions)
            elif recordType == lbsnCity().DESCRIPTOR.name:
                insert_sql = f'''
                            INSERT INTO data."city" ({self.db_mapping.get_header_for_type(recordType)})
                            VALUES {values_str}
                            ON CONFLICT (origin_id,city_guid)
                            DO UPDATE SET
                                name = COALESCE(EXCLUDED.name, data."city".name),
                                name_alternatives = COALESCE((SELECT array_remove(altNamesNewArray,data."city".name) from extensions.mergeArrays(EXCLUDED.name_alternatives, data."city".name_alternatives) AS altNamesNewArray), ARRAY[]::text[]),
                                geom_center = COALESCE(EXCLUDED.geom_center, data."city".geom_center),
                                geom_area = COALESCE(EXCLUDED.geom_area, data."city".geom_area),
                                url = COALESCE(EXCLUDED.url, data."city".url),
                                country_guid = COALESCE(EXCLUDED.country_guid, data."city".country_guid),
                                sub_type = COALESCE(EXCLUDED.sub_type, data."city".sub_type);
                            '''
            elif recordType == lbsnPlace().DESCRIPTOR.name:
                insert_sql = f'''
                            INSERT INTO data."place" ({self.db_mapping.get_header_for_type(recordType)})
                            VALUES {values_str}
                            ON CONFLICT (origin_id,place_guid)
                            DO UPDATE SET
                                name = COALESCE(EXCLUDED.name, data."place".name),
                                name_alternatives = COALESCE((SELECT array_remove(altNamesNewArray,data."place".name) from extensions.mergeArrays(EXCLUDED.name_alternatives, data."place".name_alternatives) AS altNamesNewArray), ARRAY[]::text[]),
                                geom_center = COALESCE(EXCLUDED.geom_center, data."place".geom_center),
                                geom_area = COALESCE(EXCLUDED.geom_area, data."place".geom_area),
                                url = COALESCE(EXCLUDED.url, data."place".url),
                                city_guid = COALESCE(EXCLUDED.city_guid, data."place".city_guid),
                                post_count = GREATEST(COALESCE(EXCLUDED.post_count, data."place".post_count), COALESCE(data."place".post_count, EXCLUDED.post_count));
                            '''
            elif recordType == lbsnUserGroup().DESCRIPTOR.name:
                insert_sql = f'''
                            INSERT INTO data."user_groups" ({self.db_mapping.get_header_for_type(recordType)})
                            VALUES {values_str}
                            ON CONFLICT (origin_id, usergroup_guid)
                            DO UPDATE SET
                                usergroup_name = COALESCE(EXCLUDED.usergroup_name, data."user_groups".usergroup_name),
                                usergroup_description = COALESCE(EXCLUDED.usergroup_description, data."user_groups".usergroup_description),
                                member_count = GREATEST(COALESCE(EXCLUDED.member_count, data."user_groups".member_count), COALESCE(data."user_groups".member_count, EXCLUDED.member_count)),
                                usergroup_createdate = COALESCE(EXCLUDED.usergroup_createdate, data."user_groups".usergroup_createdate),
                                user_owner = COALESCE(EXCLUDED.user_owner, data."user_groups".user_owner);
                            '''
                            # No coalesce for user: in case user changes or removes information, this should also be removed from the record
            elif recordType == lbsnUser().DESCRIPTOR.name:
                insert_sql = f'''
                            INSERT INTO data."user" ({self.db_mapping.get_header_for_type(recordType)})
                            VALUES {values_str}
                            ON CONFLICT (origin_id, user_guid)
                            DO UPDATE SET
                                user_name = COALESCE(EXCLUDED.user_name, data."user".user_name),
                                user_fullname = COALESCE(EXCLUDED.user_fullname, data."user".user_fullname),
                                follows = GREATEST(COALESCE(EXCLUDED.follows, data."user".follows), COALESCE(data."user".follows, EXCLUDED.follows)),
                                followed = GREATEST(COALESCE(EXCLUDED.followed, data."user".followed), COALESCE(data."user".followed, EXCLUDED.followed)),
                                group_count = GREATEST(COALESCE(EXCLUDED.group_count, data."user".group_count), COALESCE(data."user".group_count, EXCLUDED.group_count)),
                                biography = COALESCE(EXCLUDED.biography, data."user".biography),
                                post_count = GREATEST(COALESCE(EXCLUDED.post_count, "user".post_count), COALESCE(data."user".post_count, EXCLUDED.post_count)),
                                is_private = COALESCE(EXCLUDED.is_private, data."user".is_private),
                                url = COALESCE(EXCLUDED.url, data."user".url),
                                is_available = COALESCE(EXCLUDED.is_available, data."user".is_available),
                                user_language = COALESCE(EXCLUDED.user_language, data."user".user_language),
                                user_location = COALESCE(EXCLUDED.user_location, data."user".user_location),
                                user_location_geom = COALESCE(EXCLUDED.user_location_geom, data."user".user_location_geom),
                                liked_count = GREATEST(COALESCE(EXCLUDED.liked_count, data."user".liked_count), COALESCE(data."user".liked_count, EXCLUDED.liked_count)),
                                active_since = COALESCE(EXCLUDED.active_since, data."user".active_since),
                                profile_image_url = COALESCE(EXCLUDED.profile_image_url, data."user".profile_image_url),
                                user_timezone = COALESCE(EXCLUDED.user_timezone, data."user".user_timezone),
                                user_utc_offset = COALESCE(EXCLUDED.user_utc_offset, data."user".user_utc_offset),
                                user_groups_member = COALESCE(extensions.mergeArrays(EXCLUDED.user_groups_member, data."user".user_groups_member), ARRAY[]::text[]),
                                user_groups_follows = COALESCE(extensions.mergeArrays(EXCLUDED.user_groups_follows, data."user".user_groups_follows), ARRAY[]::text[]);
                            '''
            elif recordType == lbsnPost().DESCRIPTOR.name:
                insert_sql = f'''
                            INSERT INTO data."post" ({self.db_mapping.get_header_for_type(recordType)})
                            VALUES {values_str}
                            ON CONFLICT (origin_id, post_guid)
                            DO UPDATE SET
                                post_latlng = COALESCE(EXCLUDED.post_latlng, data."post".post_latlng),
                                place_guid = COALESCE(EXCLUDED.place_guid, data."post".place_guid),
                                city_guid = COALESCE(EXCLUDED.city_guid, data."post".city_guid),
                                country_guid = COALESCE(EXCLUDED.country_guid, data."post".country_guid),
                                post_geoaccuracy = COALESCE(EXCLUDED.post_geoaccuracy, data."post".post_geoaccuracy),
                                user_guid = COALESCE(EXCLUDED.user_guid, data."post".user_guid),
                                post_create_date = COALESCE(EXCLUDED.post_create_date, data."post".post_create_date),
                                post_publish_date = COALESCE(EXCLUDED.post_publish_date, data."post".post_publish_date),
                                post_body = COALESCE(EXCLUDED.post_body, data."post".post_body),
                                post_language = COALESCE(EXCLUDED.post_language, data."post".post_language),
                                user_mentions = COALESCE(EXCLUDED.user_mentions, data."post".user_mentions),
                                hashtags = COALESCE(extensions.mergeArrays(EXCLUDED.hashtags, data."post".hashtags), ARRAY[]::text[]),
                                emoji = COALESCE(extensions.mergeArrays(EXCLUDED.emoji, data."post".emoji), ARRAY[]::text[]),
                                post_like_count = COALESCE(EXCLUDED.post_like_count, data."post".post_like_count),
                                post_comment_count = COALESCE(EXCLUDED.post_comment_count, data."post".post_comment_count),
                                post_views_count = COALESCE(EXCLUDED.post_views_count, data."post".post_views_count),
                                post_title = COALESCE(EXCLUDED.post_title, data."post".post_title),
                                post_thumbnail_url = COALESCE(EXCLUDED.post_thumbnail_url, data."post".post_thumbnail_url),
                                post_url = COALESCE(EXCLUDED.post_url, data."post".post_url),
                                post_type = COALESCE(EXCLUDED.post_type, data."post".post_type),
                                post_filter = COALESCE(EXCLUDED.post_filter, data."post".post_filter),
                                post_quote_count = COALESCE(EXCLUDED.post_quote_count, data."post".post_quote_count),
                                post_share_count = COALESCE(EXCLUDED.post_share_count, data."post".post_share_count),
                                input_source = COALESCE(EXCLUDED.input_source, data."post".input_source);
                            '''
            elif recordType == lbsnPostReaction().DESCRIPTOR.name:
                insert_sql = f'''
                            INSERT INTO data."post_reaction" ({self.db_mapping.get_header_for_type(recordType)})
                            VALUES {values_str}
                            ON CONFLICT (origin_id, reaction_guid)
                            DO UPDATE SET
                                reaction_latlng = COALESCE(EXCLUDED.reaction_latlng, data."post_reaction".reaction_latlng),
                                user_guid = COALESCE(EXCLUDED.user_guid, data."post_reaction".user_guid),
                                referencedPost_guid = COALESCE(EXCLUDED.referencedPost_guid, data."post_reaction".referencedPost_guid),
                                referencedPostreaction_guid = COALESCE(EXCLUDED.referencedPostreaction_guid, data."post_reaction".referencedPostreaction_guid),
                                reaction_type = COALESCE(EXCLUDED.reaction_type, data."post_reaction".reaction_type),
                                reaction_date = COALESCE(EXCLUDED.reaction_date, data."post_reaction".reaction_date),
                                reaction_content = COALESCE(EXCLUDED.reaction_content, data."post_reaction".reaction_content),
                                reaction_like_count = COALESCE(EXCLUDED.reaction_like_count, data."post_reaction".reaction_like_count),
                                user_mentions = COALESCE(extensions.mergeArrays(EXCLUDED.user_mentions, data."post_reaction".user_mentions), ARRAY[]::text[]);
                            '''
            self.submitBatch(insert_sql)

    def submitLbsnRelationships(self):
        # submit relationships of different types record[1] is the PostgresQL formatted list of values, record[0] is the type of relationship that determines the table selection
        selectFriends = [relationship[1] for relationship in self.batchedRecords[lbsnRelationship().DESCRIPTOR.name] if relationship[0] == "isfriend"]
        if selectFriends:
            if self.storeCSV:
                self.csv_output.store_append_batch_to_csv(selectFriends, self.countRound, '_user_friends_user')
            if self.dbCursor:
                args_isFriend = ','.join(selectFriends)
                insert_sql = f'''
                                INSERT INTO relations."_user_friends_user" ({self.typeNamesHeaderDict["_user_friends_user"]})
                                VALUES {args_isFriend}
                                ON CONFLICT (origin_id, user_guid, friend_guid)
                                DO NOTHING
                            '''
                self.submitBatch(insert_sql)
        selectConnected = [relationship[1] for relationship in self.batchedRecords[lbsnRelationship().DESCRIPTOR.name] if relationship[0] == "isconnected"]
        if selectConnected:
            if self.storeCSV:
                self.csv_output.store_append_batch_to_csv(selectConnected, self.countRound, '_user_connectsto_user')
            if self.dbCursor:
                args_isConnected = ','.join(selectConnected)
                insert_sql = f'''
                                INSERT INTO relations."_user_connectsto_user" ({self.typeNamesHeaderDict["_user_connectsto_user"]})
                                VALUES {args_isConnected}
                                ON CONFLICT (origin_id, user_guid, connectedto_user_guid)
                                DO NOTHING
                            '''
                self.submitBatch(insert_sql)
        selectUserGroupMember = [relationship[1] for relationship in self.batchedRecords[lbsnRelationship().DESCRIPTOR.name] if relationship[0] == "ingroup"]
        if selectUserGroupMember:
            if self.storeCSV:
                self.csv_output.store_append_batch_to_csv(selectUserGroupMember, self.countRound, '_user_memberof_group')
            if self.dbCursor:
                args_isInGroup = ','.join(selectUserGroupMember)
                insert_sql = f'''
                                INSERT INTO relations."_user_memberof_group" ({self.typeNamesHeaderDict["_user_memberof_group"]})
                                VALUES {args_isInGroup}
                                ON CONFLICT (origin_id, user_guid, group_guid)
                                DO NOTHING
                            '''
                self.submitBatch(insert_sql)
        selectUserGroupMember = [relationship[1] for relationship in self.batchedRecords[lbsnRelationship().DESCRIPTOR.name] if relationship[0] == "followsgroup"]
        if selectUserGroupMember:
            if self.storeCSV:
               self.csv_output.store_append_batch_to_csv(selectUserGroupMember, self.countRound, '_user_follows_group')
            if self.dbCursor:
                args_isInGroup = ','.join(selectUserGroupMember)
                insert_sql = f'''
                                INSERT INTO relations."_user_follows_group" ({self.typeNamesHeaderDict["_user_follows_group"]})
                                VALUES {args_isInGroup}
                                ON CONFLICT (origin_id, user_guid, group_guid)
                                DO NOTHING
                            '''
                self.submitBatch(insert_sql)
        selectUserMentions = [relationship[1] for relationship in self.batchedRecords[lbsnRelationship().DESCRIPTOR.name] if relationship[0] == "mentions_user"]
        if selectUserMentions:
            if self.storeCSV:
                self.csv_output.store_append_batch_to_csv(selectUserMentions, self.countRound, '_user_mentions_user')
            if self.dbCursor:
                args_isInGroup = ','.join(selectUserMentions)
                insert_sql = f'''
                                INSERT INTO relations."_user_mentions_user" ({self.typeNamesHeaderDict["_user_mentions_user"]})
                                VALUES {args_isInGroup}
                                ON CONFLICT (origin_id, user_guid, mentioneduser_guid)
                                DO NOTHING
                            '''
                self.submitBatch(insert_sql)

    def submitBatch(self,insert_sql):
        ## Needs testing: is using Savepoint for each insert slower than rolling back entire commit?
        ## for performance, see https://stackoverflow.com/questions/12206600/how-to-speed-up-insertion-performance-in-postgresql
        ## or this: https://stackoverflow.com/questions/8134602/psycopg2-insert-multiple-rows-with-one-query
        self.dbCursor.execute("SAVEPOINT submit_recordBatch")
        tsuccessful = False
        while not tsuccessful:
            try:
                self.dbCursor.execute(insert_sql)
            except psycopg2.IntegrityError as e:
                if '(post_language)' in e.diag.message_detail or '(user_language)' in e.diag.message_detail:
                    # If language does not exist, we'll trust Twitter and add this to our language list
                    missingLanguage = e.diag.message_detail.partition("language)=(")[2].partition(") is not present")[0]
                    print(f'TransactionIntegrityError, inserting language "{missingLanguage}" first..               ')
                    self.dbCursor.execute("ROLLBACK TO SAVEPOINT submit_recordBatch")
                    insert_language_sql = '''
                           INSERT INTO data."language" (language_short,language_name,language_name_de)
                           VALUES (%s,NULL,NULL);
                           '''
                    self.dbCursor.execute(insert_language_sql,(missingLanguage,))
                else:
                    sys.exit(f'{e}')
            except ValueError as e:
                self.log.warning(f'{e}')
                input("Press Enter to continue... (entry will be skipped)")
                self.log.warning(f'{insert_sql}')
                input("args:... ")
                self.log.warning(f'{args_str}')
                self.dbCursor.execute("ROLLBACK TO SAVEPOINT submit_recordBatch")
                tsuccessful = True
            except psycopg2.ProgrammingError as e:
                sys.exit(insert_sql)
            else:
                #self.count_affected += self.dbCursor.rowcount # monitoring
                self.dbCursor.execute("RELEASE SAVEPOINT submit_recordBatch")
                tsuccessful = True

    def prepareSQLEscapedValues(self, *args):
        # dynamically construct sql value injection
        # e.g. record_sql = '''(%s,%s,%s,%s,%s,%s,%s)'''
        record_sql = f'''{','.join('%s' for x in range(0, len(args)))}'''
        # inject values
        preparedSQLRecord = self.dbCursor.mogrify(record_sql, tuple(args))
        #mogrify returns a byte object, we decode it so it can be used as a string again
        preparedSQLRecord = preparedSQLRecord.decode()
        return preparedSQLRecord

    def sortCleanProtoRepeatedField(self, record):
        # remove duplicate values in repeated field, sort alphabetically
        # needed for unique compare
        for descriptor in record.DESCRIPTOR.fields:
            if descriptor.label == descriptor.LABEL_REPEATED:
                x = getattr(record, descriptor.name)
                if x and not isinstance(x, RepeatedCompositeFieldContainer):
                    xCleaned = set(x)
                    xSorted = sorted(xCleaned)
                    #Complete clear of repeated field
                    for key in range(0, len(x)):
                        x.pop()
                    # add sorted list
                    x.extend(xSorted)

    def finalize(self):
        """ Final procedure calls:
            - clean and merge csv batches
        """
        if self.storeCSV:
            self.csv_output.clean_csv_batches(self.batchedRecords)

