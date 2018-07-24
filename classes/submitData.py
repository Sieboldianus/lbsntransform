# -*- coding: utf-8 -*-

import psycopg2
from classes.helperFunctions import helperFunctions
from classes.helperFunctions import lbsnRecordDicts as lbsnRecordDicts
#from lbsn2structure import *
from lbsnstructure.structure_pb2 import *
##from descriptor_pb2 import DescriptorProto
from lbsnstructure.external.timestamp_pb2 import Timestamp
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

from heapq import merge as heapqMerge
from operator import itemgetter
from contextlib import ExitStack

from google.protobuf.internal import encoder
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
import base64

class lbsnDB():
    def __init__(self, dbCursor = None,
                 dbConnection = None,
                 commit_volume = 10000,
                 disableReactionPostReferencing = 0, storeCSV = None, CSVsuppressLinebreaks = True):
        self.dbCursor = dbCursor
        self.dbConnection = dbConnection
        if not self.dbCursor:
            print("CSV Output Mode.")
        self.count_entries_commit = 0
        self.count_entries_store = 0
        self.count_affected = 0
        self.commit_volume = commit_volume
        self.store_volume = 500000
        self.storeCSVPart = 0
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
        self.dictTypeSwitcher = { # create protoBuf messages by name
            lbsnCountry().DESCRIPTOR.name: lbsnCountry(),
            lbsnCity().DESCRIPTOR.name: lbsnCity(),
            lbsnPlace().DESCRIPTOR.name: lbsnPlace(),
            lbsnUser().DESCRIPTOR.name: lbsnUser(),
            lbsnUserGroup().DESCRIPTOR.name:  lbsnUserGroup(),
            lbsnPost().DESCRIPTOR.name: lbsnPost(),
            lbsnPostReaction().DESCRIPTOR.name: lbsnPostReaction(),
            lbsnRelationship().DESCRIPTOR.name: lbsnRelationship()
        }
        self.countRound = 0
        self.batchDBVolume = 100 # Records are batched and submitted in one insert with x number of records
        self.storeCSV = storeCSV
        self.headersWritten = set()
        self.CSVsuppressLinebreaks = CSVsuppressLinebreaks
        self.typeNamesHeaderDict = {lbsnCity.DESCRIPTOR.name: 'origin_id, city_guid, name, name_alternatives, geom_center, geom_area, url, country_guid, sub_type',
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
        if self.storeCSV:
            self.OutputPathFile = f'{os.getcwd()}\\02_Output\\'
            if not os.path.exists(self.OutputPathFile):
                os.makedirs(self.OutputPathFile)

    def commitChanges(self):
        if self.dbCursor:
            self.dbConnection.commit() # commit changes to db
            self.count_entries_commit = 0

    def storeChanges(self):
        if self.storeCSV:
            self.cleanCSVBatches()
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

    def funcPrepareSelector(self, record):
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
            preparedRecord = self.funcPrepareSelector(record)
            if preparedRecord:
                preparedRecords.append(preparedRecord)
        return preparedRecords

    def submitLbsnRecords(self, recordType):
        preparedRecords = self.prepareRecords(recordType)
        if self.storeCSV:
            self.storeAppendCSV(recordType)
        if self.dbCursor:
            values_str = ','.join([self.prepareSQLEscapedValues(record) for record in preparedRecords])
            if recordType == lbsnCountry().DESCRIPTOR.name:
                insert_sql = f'''
                            INSERT INTO data."country" ({self.typeNamesHeaderDict[recordType]})
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
                            INSERT INTO data."city" ({self.typeNamesHeaderDict[recordType]})
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
                            INSERT INTO data."place" ({self.typeNamesHeaderDict[recordType]})
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
                            INSERT INTO data."user_groups" ({self.typeNamesHeaderDict[recordType]})
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
                            INSERT INTO data."user" ({self.typeNamesHeaderDict[recordType]})
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
                            INSERT INTO data."post" ({self.typeNamesHeaderDict[recordType]})
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
                            INSERT INTO data."post_reaction" ({self.typeNamesHeaderDict[recordType]})
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

    def prepareLbsnCountry(self, record):
        # Get common attributes for place types Place, City and Country
        placeRecord = placeAttrShared(record)
        preparedRecord = (placeRecord.OriginID,
                          placeRecord.Guid,
                          placeRecord.name,
                          placeRecord.name_alternatives,
                          helperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_center),
                          helperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_area),
                          placeRecord.url)
        return preparedRecord

    def prepareLbsnCity(self, record):
        placeRecord = placeAttrShared(record)
        countryGuid = helperFunctions.null_check(record.country_pkey.id)
        subType = helperFunctions.null_check(record.sub_type)
        preparedRecord = (placeRecord.OriginID,
                          placeRecord.Guid,
                          placeRecord.name,
                          placeRecord.name_alternatives,
                          helperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_center),
                          helperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_area),
                          placeRecord.url,
                          countryGuid,
                          subType)
        return preparedRecord

    def prepareLbsnPlace(self, record):
        placeRecord = placeAttrShared(record)
        cityGuid = helperFunctions.null_check(record.city_pkey.id)
        postCount = helperFunctions.null_check(record.post_count)
        preparedRecord = (placeRecord.OriginID,
                          placeRecord.Guid,
                          placeRecord.name,
                          placeRecord.name_alternatives,
                          helperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_center),
                          helperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_area),
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
                          helperFunctions.returnEWKBFromGeoTEXT(userRecord.user_location_geom),
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
                          helperFunctions.returnEWKBFromGeoTEXT(postRecord.post_latlng),
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
                          helperFunctions.returnEWKBFromGeoTEXT(postReactionRecord.reaction_latlng),
                          postReactionRecord.user_guid,
                          postReactionRecord.referencedPost,
                          postReactionRecord.referencedPostreaction,
                          postReactionRecord.reaction_type,
                          postReactionRecord.reaction_date,
                          postReactionRecord.reaction_content,
                          postReactionRecord.reaction_like_count,
                          postReactionRecord.user_mentions)
        return preparedRecord

    def submitLbsnRelationships(self):
        # submit relationships of different types record[1] is the PostgresQL formatted list of values, record[0] is the type of relationship that determines the table selection
        selectFriends = [relationship[1] for relationship in self.batchedRecords[lbsnRelationship().DESCRIPTOR.name] if relationship[0] == "isfriend"]
        if selectFriends:
            if self.storeCSV:
                self.storeAppendCSV(selectFriends, '_user_friends_user')
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
                self.storeAppendCSV(selectConnected, '_user_connectsto_user')
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
                self.storeAppendCSV(selectUserGroupMember, '_user_memberof_group')
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
                self.storeAppendCSV(selectUserGroupMember, '_user_follows_group')
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
                self.storeAppendCSV(selectUserMentions, '_user_mentions_user')
            if self.dbCursor:
                args_isInGroup = ','.join(selectUserMentions)
                insert_sql = f'''
                                INSERT INTO relations."_user_mentions_user" ({self.typeNamesHeaderDict["_user_mentions_user"]})
                                VALUES {args_isInGroup}
                                ON CONFLICT (origin_id, user_guid, mentioneduser_guid)
                                DO NOTHING
                            '''
                self.submitBatch(insert_sql)
    #??
    def prepareLbsnRelationship(self, record):
        relationshipRecord = relationshipAttrShared(record)
        preparedTypeRecordTuple = (relationshipRecord.relType,
                          self.prepareRecordValues(relationshipRecord.OriginID,
                          relationshipRecord.Guid,
                          relationshipRecord.Guid_Rel))
        return preparedTypeRecordTuple

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

    ###########################
    ### CSV Functions Below ###
    ###########################

    def storeAppendCSV(self, typeName, pgCopyFormat = False):
        records = self.batchedRecords[typeName]
        filePath = f'{self.OutputPathFile}{typeName}-{self.countRound:03d}.csv'
        with open(filePath, 'a', encoding='utf8') as f:
            #csvOutput = csv.writer(f, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for record in records:
                serializedRecord_b64 = self.serializeEncodeRecord(record)
                f.write(f'{record.pkey.id},{serializedRecord_b64}\n')

    def serializeEncodeRecord(self, record):
        # serializes record as string and encodes in base64 for corrupt-resistant backup/store/transfer
        serializedRecord = record.SerializeToString()
        serializedEncodedRecord = base64.b64encode(serializedRecord)
        serializedEncodedRecordUTF = serializedEncodedRecord.decode("utf-8")
        return serializedEncodedRecordUTF

    #def writeCSVHeader(self, typeName):
    #    # create files and write headers
    #    #for typename, header in self.typeNamesHeaderDict.items():
    #    header = self.typeNamesHeaderDict[typeName]
    #    csvOutput = open(f'{self.OutputPathFile}{typeName}_{self.countRound:03d}.csv', 'w', encoding='utf8')
    #    csvOutput.write("%s\n" % header)

    def cleanCSVBatches(self):
        # function that merges all output streams at end
        x=0
        self.storeCSVPart += 1
        print('Cleaning and merging output files..')
        for typeName in self.batchedRecords:
            x+= 1
            filelist = glob(f'{self.OutputPathFile}{typeName}-*.csv')
            if filelist:
                self.sortFiles(filelist,typeName)
                if len(filelist) > 1:
                    print(f'Cleaning & merging output files..{x}/{len(self.batchedRecords)}', end='\r')
                    self.mergeFiles(filelist,typeName)
                else:
                    # no need to merge files if only one round
                    new_filename = filelist[0].replace('_001','001Proto')
                    if os.path.isfile(new_filename):
                        os.remove(new_filename)
                    if os.path.isfile(filelist[0]):
                        os.rename(filelist[0], new_filename)
                self.removeMergeDuplicateRecords_FormatCSV(typeName)

    def sortFiles(self, filelist, typeName):
        for f in filelist:
            with open(f,'r+', encoding='utf8') as batchFile:
                #skip header
                #header = batchFile.readline()
                lines = batchFile.readlines()
                # sort by first column
                lines.sort(key=lambda a_line: a_line.split()[0])
                #lines.sort()
                batchFile.seek(0)
                # delete original records in file
                batchFile.truncate()
                # write sorted records
                #batchFile.writeline(header)
                for line in lines:
                    batchFile.write(line)

    def mergeFiles(self, filelist, typeName):
        with ExitStack() as stack:
            files = [stack.enter_context(open(fname, encoding='utf8')) for fname in filelist]
            with open(f'{self.OutputPathFile}{typeName}_Part{self.countRound:03d}Proto.csv','w', encoding='utf8') as mergedFile:
                mergedFile.writelines(heapqMerge(*files))
        for file in filelist:
            os.remove(file)

    def createProtoByDescriptorName(self, descName):
        newRecord = self.dictTypeSwitcher[descName]
        return newRecord

    def parseMessage(self,msgType,stringMessage):
            #result_class = reflection.GeneratedProtocolMessageType(msgType,(stringMessage,),{'DESCRIPTOR': descriptor, '__module__': None})
            ParseMessage
            msgClass=lbsnstructure.Structure_pb2[msgType]
            message=msgClass()
            message.ParseFromString(stringMessage)
            return message

    def removeMergeDuplicateRecords_FormatCSV(self, typeName):
        def getRecordID_From_base64EncodedString(line):
            record = getRecord_From_base64EncodedString(line)
            return record.pkey.id
        def getRecord_From_base64EncodedString(line):
            record = self.createProtoByDescriptorName(typeName)
            record.ParseFromString(base64.b64decode(line))#.strip("\n"))
            return record
        def mergeRecords(duplicateRecordLines):
            if len(duplicateRecordLines) > 1:
                # first do a simple compare/unique
                uniqueRecords = set(duplicateRecordLines)
                if len(uniqueRecords) > 1:
                    #input(f'Len: {len(uniqueRecords)} : {uniqueRecords}')
                    # if more than one unqiue record infos, get first and deep-compare-merge with following
                    prevDuprecord = getRecord_From_base64EncodedString(duplicateRecordLines[0])
                    for duprecord in duplicateRecordLines[1:]:
                        # merge current record with previous until no more found
                        # will modify/overwrite prevDuprecord
                        helperFunctions.MergeExistingRecords(prevDuprecord,getRecord_From_base64EncodedString(duprecord))
                    mergedRecord = self.serializeEncodeRecord(prevDuprecord)
                else:
                    # take first element
                    mergedRecord = next(iter(uniqueRecords))
            else:
                mergedRecord = duplicateRecordLines[0]
            return mergedRecord
        def formatB64EncodedRecordForCSV(record_b64):
            record = getRecord_From_base64EncodedString(record_b64)
            # convert Protobuf to Value list
            preparedRecord = self.funcPrepareSelector(record)
            formattedValueList = []
            for value in preparedRecord:
                # CSV Writer can't produce CSV that can be directly read by Postgres with /Copy
                # Format some types manually (e.g. arrays, null values)
                if isinstance(value, list):
                    value = '{' + ",".join(value) + '}'
                elif self.CSVsuppressLinebreaks and isinstance(value, str):
                    # replace linebreaks by actual string so we can use heapqMerge to merge line by line
                    value = value.replace('\n','\\n').replace('\r', '\\r')
                formattedValueList.append(value)
            return formattedValueList
        def cleanMergedFile(mergedFile, cleanedMergedFile):
            dupsremoved = 0
            with mergedFile, cleanedMergedFile, cleanedMergedFileCopy:
                header = self.typeNamesHeaderDict[typeName]
                cleanedMergedFileCopy.write("%s\n" % header)
                csvOutput = csv.writer(cleanedMergedFileCopy, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                # start readlines/compare
                previousRecord_id, previousRecord_b64 = next(mergedFile).split(',', 1)
                # strip linebreak from line ending
                previousRecord_b64 = previousRecord_b64.strip()
                duplicateRecordLines = []
                for line in mergedFile:
                    record_id, record_b64 = line.split(',', 1)
                    # strip linebreak from line ending
                    record_b64 = record_b64.strip()
                    if record_id == previousRecord_id:
                        # if duplicate, add to list to merge later
                        duplicateRecordLines.extend((previousRecord_b64, record_b64))
                        continue
                    else:
                        # if different id, do merge [if necessary], then continue processing
                        if duplicateRecordLines:
                            # add/overwrite new record line
                            # write merged record and continue
                            mergedRecord_b64 = mergeRecords(duplicateRecordLines)
                            dupsremoved += len(duplicateRecordLines) - 1
                            duplicateRecordLines = []
                            previousRecord_b64 = mergedRecord_b64
                    cleanedMergedFile.write(f'{previousRecord_id},{previousRecord_b64}\n')
                    formattedValueList = formatB64EncodedRecordForCSV(previousRecord_b64)
                    csvOutput.writerow(formattedValueList)
                    previousRecord_id = record_id
                    previousRecord_b64 = record_b64
                # finally
                if duplicateRecordLines:
                    finalMergedRecord = mergeRecords(duplicateRecordLines)
                else:
                    finalMergedRecord = previousRecord_b64
                cleanedMergedFile.write(f'{previousRecord_id},{finalMergedRecord}\n')
                formattedValueList = formatB64EncodedRecordForCSV(finalMergedRecord)
                csvOutput.writerow(formattedValueList)
            print(f'{typeName} Duplicates Merged: {dupsremoved}                             ')
        # main
        mergedFilename = f'{self.OutputPathFile}{typeName}{self.countRound:03d}Proto.csv'
        cleanedMergedFilename = f'{self.OutputPathFile}{typeName}{self.countRound:03d}_cleaned.csv'
        cleanedMergedFilename_CSV = f'{self.OutputPathFile}{typeName}{self.countRound:03d}pgCSV.csv'
        if os.path.isfile(mergedFilename):
            mergedFile = open(mergedFilename,'r', encoding='utf8')
            cleanedMergedFile = open(cleanedMergedFilename,'w', encoding='utf8')
            cleanedMergedFileCopy = open(cleanedMergedFilename_CSV,'w', encoding='utf8')
            cleanMergedFile(mergedFile, cleanedMergedFile)
            os.remove(mergedFilename)
            os.rename(cleanedMergedFilename, mergedFilename)

class placeAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id # = 3
        self.Guid = record.pkey.id
        self.name = helperFunctions.null_check(record.name)
        # because ProtoBuf Repeated Field does not support distinct rule, we remove any duplicates in list fields prior to submission here
        self.name_alternatives = list(set(record.name_alternatives))
        if self.name and self.name in self.name_alternatives:
            self.name_alternatives.remove(self.name)
        self.url = helperFunctions.null_check(record.url)
        self.geom_center = helperFunctions.null_check(record.geom_center)
        self.geom_area = helperFunctions.null_check(record.geom_area)

class userAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.user_name = helperFunctions.null_check(record.user_name)
        self.user_fullname = helperFunctions.null_check(record.user_fullname)
        self.follows = helperFunctions.null_check(record.follows)
        self.followed = helperFunctions.null_check(record.followed)
        self.group_count = helperFunctions.null_check(record.group_count)
        self.biography = helperFunctions.null_check(record.biography)
        self.post_count = helperFunctions.null_check(record.post_count)
        self.url = helperFunctions.null_check(record.url)
        self.is_private = helperFunctions.null_check(record.is_private)
        self.is_available = helperFunctions.null_check(record.is_available)
        self.user_language = helperFunctions.null_check(record.user_language.language_short)
        self.user_location = helperFunctions.null_check(record.user_location)
        self.user_location_geom = helperFunctions.null_check(record.user_location_geom)
        self.liked_count = helperFunctions.null_check(record.liked_count)
        self.active_since = helperFunctions.null_check_datetime(record.active_since)
        self.profile_image_url = helperFunctions.null_check(record.profile_image_url)
        self.user_timezone = helperFunctions.null_check(record.user_timezone)
        self.user_utc_offset = helperFunctions.null_check(record.user_utc_offset)
        self.user_groups_member = list(set(record.user_groups_member))
        self.user_groups_follows = list(set(record.user_groups_follows))

class userGroupAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.usergroup_name = helperFunctions.null_check(record.usergroup_name)
        self.usergroup_description = helperFunctions.null_check(record.usergroup_description)
        self.member_count = helperFunctions.null_check(record.member_count)
        self.usergroup_createdate = helperFunctions.null_check_datetime(record.usergroup_createdate)
        self.user_owner = helperFunctions.null_check(record.user_owner_pkey.id)

class postAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.post_latlng = helperFunctions.null_check(record.post_latlng)
        self.place_guid = helperFunctions.null_check(record.place_pkey.id)
        self.city_guid = helperFunctions.null_check(record.city_pkey.id)
        self.country_guid = helperFunctions.null_check(record.country_pkey.id)
        self.post_geoaccuracy = helperFunctions.null_check(lbsnPost().PostGeoaccuracy.Name(record.post_geoaccuracy)).lower()
        self.user_guid = helperFunctions.null_check(record.user_pkey.id)
        self.post_create_date = helperFunctions.null_check_datetime(record.post_create_date)
        self.post_publish_date = helperFunctions.null_check_datetime(record.post_publish_date)
        self.post_body = helperFunctions.null_check(record.post_body)
        self.post_language = helperFunctions.null_check(record.post_language.language_short)
        self.user_mentions = list(set([pkey.id for pkey in record.user_mentions_pkey]))
        self.hashtags = list(set(record.hashtags))
        self.emoji = list(set(record.emoji))
        self.post_like_count = helperFunctions.null_check(record.post_like_count)
        self.post_comment_count = helperFunctions.null_check(record.post_comment_count)
        self.post_views_count = helperFunctions.null_check(record.post_views_count)
        self.post_title = helperFunctions.null_check(record.post_title)
        self.post_thumbnail_url = helperFunctions.null_check(record.post_thumbnail_url)
        self.post_url = helperFunctions.null_check(record.post_url)
        self.post_type = helperFunctions.null_check(lbsnPost().PostType.Name(record.post_type)).lower()
        self.post_filter = helperFunctions.null_check(record.post_filter)
        self.post_quote_count = helperFunctions.null_check(record.post_quote_count)
        self.post_share_count = helperFunctions.null_check(record.post_share_count)
        self.input_source = helperFunctions.null_check(record.input_source)

class postReactionAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.reaction_latlng = helperFunctions.null_check(record.reaction_latlng)
        self.user_guid = helperFunctions.null_check(record.user_pkey.id)
        self.referencedPost = helperFunctions.null_check(record.referencedPost_pkey.id)
        self.referencedPostreaction = helperFunctions.null_check(record.referencedPostreaction_pkey.id)
        self.reaction_type = helperFunctions.null_check(lbsnPostReaction().ReactionType.Name(record.reaction_type)).lower()
        self.reaction_date = helperFunctions.null_check_datetime(record.reaction_date)
        self.reaction_content = helperFunctions.null_check(record.reaction_content)
        self.reaction_like_count = helperFunctions.null_check(record.reaction_like_count)
        self.user_mentions = list(set([pkey.id for pkey in record.user_mentions_pkey]))

class relationshipAttrShared():
    def __init__(self, relationship):
        self.OriginID = relationship.pkey.relation_to.origin.origin_id
        self.Guid = relationship.pkey.relation_to.id
        self.Guid_Rel = relationship.pkey.relation_from.id
        self.relType = helperFunctions.null_check(lbsnRelationship().RelationshipType.Name(relationship.relationship_type)).lower()