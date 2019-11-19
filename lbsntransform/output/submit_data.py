# -*- coding: utf-8 -*-

"""
Module for storing common Proto LBSN Structure to PG DB.
"""

# pylint: disable=no-member

import logging
import os
import sys
import traceback
from collections import defaultdict
from glob import glob
from sys import exit
from typing import Any, Dict, List, Tuple, Union

import psycopg2
# for debugging only:
from google.protobuf import text_format
from google.protobuf.timestamp_pb2 import Timestamp
from psycopg2 import sql

from lbsnstructure import lbsnstructure_pb2 as lbsn

from lbsntransform.output.hll import hll_bases as hll
from lbsntransform.tools.helper_functions import HelperFunctions as HF
from lbsntransform.tools.helper_functions import LBSNRecordDicts
from lbsntransform.output.hll.hll_functions import HLLFunctions as HLF
from lbsntransform.output.hll.shared_structure_proto_hlldb import ProtoHLLMapping
from lbsntransform.output.lbsn.shared_structure_proto_lbsndb import ProtoLBSNMapping
from lbsntransform.output.hll.sql_hll import HLLSql
from lbsntransform.output.lbsn.sql_lbsn import LBSNSql
from lbsntransform.output.csv.store_csv import LBSNcsv
from lbsntransform.output.hll.base import social, spatial, temporal, topical


class LBSNTransfer():
    def __init__(self, db_cursor=None,
                 db_connection=None,
                 commit_volume=10000,
                 disable_reaction_post_ref=0,
                 store_csv=None,
                 SUPPRESS_LINEBREAKS=True,
                 dbformat_output="lbsn",
                 hllworker_cursor=None):
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
        self.batched_lbsn_records = {
            lbsn.Country.DESCRIPTOR.name: list(),
            lbsn.City.DESCRIPTOR.name: list(),
            lbsn.Place.DESCRIPTOR.name: list(),
            lbsn.User.DESCRIPTOR.name: list(),
            lbsn.UserGroup.DESCRIPTOR.name: list(),
            lbsn.Post.DESCRIPTOR.name: list(),
            lbsn.PostReaction.DESCRIPTOR.name: list(),
            lbsn.Relationship.DESCRIPTOR.name: list()
        }
        # dynamially register base classes from base module
        hll.register_classes()
        # this is the global dict of measures that will be collected,
        # bases not registered here will not be measured
        self.batched_hll_records = {
            spatial.LatLngBase.NAME: dict(),
            spatial.PlaceBase.NAME: dict(),
            temporal.DateBase.NAME: dict(),
            temporal.MonthBase.NAME: dict(),
            temporal.YearBase.NAME: dict(),
            topical.TermBase.NAME: dict(),
            topical.HashtagBase.NAME: dict(),
        }
        self.count_round = 0
        # Records are batched and submitted in
        # one insert with x number of records
        self.batch_db_volume = 100
        self.store_csv = store_csv
        self.headers_written = set()
        # self.CSVsuppressLinebreaks = CSVsuppressLinebreaks
        self.dbformat_output = dbformat_output
        if self.dbformat_output == 'lbsn':
            self.db_mapping = ProtoLBSNMapping()
        else:
            self.db_mapping = ProtoHLLMapping()
            self.hllworker_cursor = hllworker_cursor
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
                self.batched_lbsn_records)
            self.count_entries_store = 0

    def store_origin(self, origin_id, name):
        insert_sql = \
            f'''
            INSERT INTO social."origin" (
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
        g_cnt = lbsn_record_dicts.get_current_count()
        for record, type_name in lbsn_record_dicts.get_all_records():
            r_cnt += 1
            print(f'Storing {r_cnt} of {g_cnt} '
                  f'lbsn records ({type_name})..', end='\r')
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
        """Prepare batched records for submit to either LBSN or HLL db"""
        # clean duplicates in repeated Fields and Sort List
        self.sort_clean_proto_repeated_field(record)
        # store cleaned ProtoBuf records
        # LBSN or HLL output
        if self.dbformat_output == 'lbsn':
            self.batched_lbsn_records[record_type].append(
                record)
        else:
            # extract hll bases and metric from records
            hll_base_metrics = self.db_mapping.extract_hll_base_metrics(
                record, record_type)
            if hll_base_metrics is None:
                # no base metrics extracted
                return
            # update hll dicts
            self.db_mapping.update_hll_dicts(
                self.batched_hll_records, hll_base_metrics)
            # input(len(self.batched_hll_bases.get(('topical', 'term'))))
            # input(self.batched_hll_bases.get(('topical', 'term')))
        # check batched records (and submit)
        self.check_batchvolume_submit()

    def check_batchvolume_submit(self):
        """If any dict contains more values than self.batch_db_volume,
           submit/store all
        """
        for batch_list in self.batched_lbsn_records.values():
            if len(batch_list) >= self.batch_db_volume:
                self.submit_all_batches()

    def submit_all_batches(self):
        if self.dbformat_output == 'lbsn':
            self.submit_batches(self.batched_lbsn_records)
        else:
            self.submit_batches(self.batched_hll_records)

    def submit_batches(self, batched_records: Union[
            Dict[str, List[str]],
            Dict[Tuple[str, str], Dict[str, Any]]]):
        """Prepare values for each batch, format sql and submit to db"""
        for record_type, batch_item in batched_records.items():
            if batch_item:
                # if self.storeCSV and not record_type in self.headersWritten:
                #    self.writeCSVHeader(record_type)
                #    self.headersWritten.add(record_type)
                func_select = self.get_prepare_records_func(
                    self.dbformat_output)
                prepared_records = func_select(
                    record_type, batch_item)
                self.submit_records(record_type, prepared_records)
                # self.funcSubmitSelector(record_type)
                batch_item.clear()

    def get_prepare_records_func(self, dbformat_outpur: str):
        """Selector function to get prepared records (hll/lbsn)
        """
        if dbformat_outpur == 'lbsn':
            return self.get_prepared_lbsn_records
        else:
            return self.get_prepared_hll_records

    def get_prepared_lbsn_records(
            self, record_type: str,
            batch_item: List[Any]):
        """Turns propietary lbsn classes into prepared sql value tuples

        For hll output, this includes calculation of
        shards from individual items using the hll_worker
        """
        prepared_records = []
        for record_item in batch_item:
            prepared_record = self.db_mapping.func_prepare_selector(
                record_item)
            if prepared_record:
                prepared_records.append(prepared_record)
        return prepared_records

    def get_prepared_hll_records(
            self, record_type: Tuple[str, str],
            batch_item: Dict[str, Any]):
        """Turns propietary hll classes into prepared sql value tuples

        This includes calculation of shards from individual items
        using the hll_worker
        """
        hll_items = []  # (base_key, metric_key, item)
        hll_base_records = []  # (base_key, attr1, attr2)
        # the following iteration will
        # loop keys in case of dict
        # and values in case of list
        for index, record_item in enumerate(batch_item.values()):
            # get base record and value
            base = record_item.get_prepared_record()
            if base.record:
                hll_base_records.append(base.record)
                base_metric_item_tuples = HLF.concat_base_metric_item(
                    index, base.metrics)
                # format tuple-values as sql-escaped strings
                value_str = [
                    self.prepare_sqlescaped_values(record) for
                    record in base_metric_item_tuples]
                # add to global list of items to be upserted
                hll_items.extend(value_str)
        # format sql for shard generation
        # get sql escaped values list
        values_str = HF.concat_values_str([value_str for
                                           value_str in hll_items])
        # input(values_str)

        hll_shards = HLF.calculate_item_shards(
            self.hllworker_cursor, values_str)
        # input(hll_shards)
        prepared_records = HLF.concat_base_shards(
            hll_base_records, hll_shards)
        return prepared_records

    def submit_records(
            self, record_type: Union[Tuple[str, str], str],
            prepared_records: List[Tuple[Any]]):
        if self.store_csv:
            self.csv_output.store_append_batch_to_csv(
                self.batched_lbsn_records[record_type],
                self.count_round, record_type)
        if self.db_cursor:
            # get sql escaped values list
            sql_escaped_values_list = [
                self.prepare_sqlescaped_values(record) for
                record in prepared_records]
            # concat to single sql str
            values_str = HF.concat_values_str(
                sql_escaped_values_list
            )
            insert_sql = self.insert_sql_selector(values_str, record_type)
            self.submit_batch(insert_sql)

    def insert_sql_selector(
            self, values_str: str, record_type):
        """ Select function to prepare SQL insert.

        Attributes:
            record_type     type of record
            values_str      values to be inserted
        """
        if self.dbformat_output == 'lbsn':
            sql_selector = LBSNSql.type_sql_mapper()
            prepare_function = sql_selector.get(record_type)
        else:
            # hll
            prepare_function = HLLSql.hll_insertsql
        return prepare_function(values_str, record_type)

    def submitLbsnRelationships(self):
        """submit relationships of different types

        record[1] is the PostgresQL formatted list of values,
        record[0] is the type of relationship that determines
            the table selection
        """
        selectFriends = [relationship[1] for relationship in
                         self.batched_lbsn_records[lbsn.Relationship(
                         ).DESCRIPTOR.name] if relationship[0] == "isfriend"]
        if selectFriends:
            if self.store_csv:
                self.csv_output.store_append_batch_to_csv(
                    selectFriends, self.count_round, '_user_friends_user')
            if self.db_cursor:
                args_isFriend = ','.join(selectFriends)
                insert_sql = \
                    f'''
                    INSERT INTO social."_user_friends_user" (
                        {self.typeNamesHeaderDict["_user_friends_user"]})
                    VALUES {args_isFriend}
                    ON CONFLICT (origin_id, user_guid, friend_guid)
                    DO NOTHING
                    '''
                self.submit_batch(insert_sql)
        selectConnected = [relationship[1] for relationship in
                           self.batched_lbsn_records[lbsn.Relationship(
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
                        INSERT INTO social."_user_connectsto_user" (
                            {self.typeNamesHeaderDict["_user_connectsto_user"]})
                        VALUES {args_isConnected}
                        ON CONFLICT (origin_id, user_guid,
                            connectedto_user_guid)
                        DO NOTHING
                    '''
                self.submit_batch(insert_sql)
        selectUserGroupMember = [relationship[1] for relationship in
                                 self.batched_lbsn_records[lbsn.Relationship(
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
                    INSERT INTO social."_user_memberof_group" (
                        {self.typeNamesHeaderDict["_user_memberof_group"]})
                    VALUES {args_isInGroup}
                    ON CONFLICT (origin_id, user_guid, group_guid)
                    DO NOTHING
                    '''
                self.submit_batch(insert_sql)
        selectUserGroupMember = [relationship[1] for relationship in
                                 self.batched_lbsn_records[lbsn.Relationship(
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
                    INSERT INTO social."_user_follows_group" (
                        {self.typeNamesHeaderDict["_user_follows_group"]})
                    VALUES {args_isInGroup}
                    ON CONFLICT (origin_id, user_guid, group_guid)
                    DO NOTHING
                    '''
                self.submit_batch(insert_sql)
        selectUserMentions = [relationship[1] for relationship in
                              self.batched_lbsn_records[lbsn.Relationship(
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
                    INSERT INTO social."_user_mentions_user" (
                        {self.typeNamesHeaderDict["_user_mentions_user"]})
                    VALUES {args_isInGroup}
                    ON CONFLICT (origin_id, user_guid, mentioneduser_guid)
                    DO NOTHING
                    '''
                self.submit_batch(insert_sql)

    def submit_batch(self, insert_sql):
        """Submit Batch to PG DB.

        Needs testing: is using Savepoint for each insert slower
        than rolling back entire commit?
        for performance, see https://stackoverflow.com/questions/
            12206600/how-to-speed-up-insertion-performance-in-postgresql
        or this: https://stackoverflow.com/questions/8134602/
        psycopg2-insert-multiple-rows-with-one-query
        """
        tsuccessful = False
        # input(insert_sql)
        self.db_cursor.execute("SAVEPOINT submit_recordBatch")
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
                    # self.db_cursor.rollback()
                    self.db_cursor.execute(
                        "ROLLBACK TO SAVEPOINT submit_recordBatch")
                    insert_language_sql = '''
                           INSERT INTO data."language"
                            (language_short, language_name, language_name_de)
                           VALUES (%s,NULL,NULL);
                           '''
                    # submit sql to db
                    self.db_cursor.execute(
                        insert_language_sql, (missingLanguage,))
                    # commit changes so they're available when
                    # try is executed again
                    self.commit_changes()
                    # recreate SAVEPOINT after language insert
                    self.db_cursor.execute("SAVEPOINT submit_recordBatch")
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
                file = open("hll_exc.txt", "w")
                file.write(f'{e}\nINSERT SQL WAS: {insert_sql}')
                file.close()  # This close() is important
                sys.exit(f'{e}\nINSERT SQL WAS: {insert_sql}')
            except psycopg2.errors.DiskFull as e:
                input("Disk space full. Clean files and continue..")
            else:
                # executed if the try clause does not raise an exception
                self.db_cursor.execute("RELEASE SAVEPOINT submit_recordBatch")
                tsuccessful = True

    def prepare_sqlescaped_values(self, *args):
        """dynamically construct sql value injection

        e.g. record_sql = '''(%s,%s,%s,%s,%s,%s,%s)'''
        """
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
                if x and not HF.is_composite_field_container(x):
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
            self.csv_output.clean_csv_batches(self.batched_lbsn_records)
        file = open("hll.txt", "w")
        file.write(f'{self.batched_hll_records}')
        file.close()  # This close() is important
