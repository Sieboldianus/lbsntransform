# -*- coding: utf-8 -*-

"""
Module for loding data from different sources (CSV, DB, JSON etc.).
"""

import codecs
import csv
import os
import sys
import logging
import traceback
from contextlib import closing
from itertools import zip_longest
from typing import Tuple, List, Union, Iterator, Optional, IO
import psycopg2

import ntpath
import requests
from lbsnstructure import lbsnstructure_pb2 as lbsn

from ..tools.db_connection import DBConnection
from ..output.shared_structure import GeocodeLocations
from ..tools.helper_functions import HelperFunctions as HF
from .mappings.db_query import InputSQL, LBSN_SCHEMA

# type alias
LBSNObjects = Union[
    lbsn.CompositeKey, lbsn.Language, lbsn.RelationshipKey, lbsn.City,
    lbsn.Country, lbsn.Origin, lbsn.Place, lbsn.Post,
    lbsn.PostReaction, lbsn.Relationship, lbsn.User,
    lbsn.UserGroup]


class LoadData():
    """
    Class for loding data from different sources (CSV, DB, JSON etc.).
    """

    def __init__(
            self, importer=None, is_local_input=None,
            startwith_db_rownumber=None,
            skip_until_file=None, cursor_input=None, input_path=None,
            recursive_load=None, local_file_type=None,
            endwith_db_rownumber=None, is_stacked_json=None,
            is_line_separated_json=None, csv_delim=None,
            input_lbsn_type=None, dbformat_input=None, geocode_locations=None,
            ignore_input_source_list=None, disable_reactionpost_ref=None,
            map_relations=None, transfer_reactions=None,
            ignore_non_geotagged=None, min_geoaccuracy=None, source_web=None,
            zip_records=None, skip_until_record=None,
            exclude_lbsn_objects=None):
        self.is_local_input = is_local_input
        self.start_number = 1
        self.continue_number = None
        self.skip_until_record = None
        if not self.is_local_input:
            # Start Value, Modify to continue from last processing
            self.continue_number = startwith_db_rownumber
            self.start_number = startwith_db_rownumber
        else:
            self.continue_number = 0
            if skip_until_file is not None:
                self.continue_number = skip_until_file
            self.skip_until_record = skip_until_record
        self.source_web = source_web
        if zip_records is None:
            zip_records = False
        self.zip_records = zip_records
        self.cursor_input = cursor_input
        if self.is_local_input and not self.source_web:
            self.filelist = LoadData._read_local_files(
                input_path=input_path, recursive_load=recursive_load,
                local_file_type=local_file_type,
                skip_until_file=skip_until_file)
        elif self.is_local_input and self.source_web:
            self.filelist = input_path
        self.finished = False
        self.dbformat_input = dbformat_input

        self.db_row_number = 0
        self.endwith_db_rownumber = endwith_db_rownumber
        self.is_stacked_json = is_stacked_json
        self.is_line_separated_json = is_line_separated_json
        self.local_file_type = local_file_type
        self.csv_delim = csv_delim
        self.file_format = local_file_type
        self.input_lbsn_type = input_lbsn_type
        self.start_id = None
        if exclude_lbsn_objects is None:
            exclude_lbsn_objects = []
        self.exclude_lbsn_objects = exclude_lbsn_objects
        self.count_glob = 0
        self.current_source = None
        # self.transferlimit = cfg.transferlimit
        # Optional Geocoding
        self.geocode_dict = None
        if geocode_locations:
            self.geocode_dict = LoadData.load_geocodes(
                geocode_locations)
        # Optional ignore input sources
        self.ignore_sources_set = None
        if ignore_input_source_list:
            self.ignore_sources_set = LoadData.load_ignore_sources(
                ignore_input_source_list)

        # initialize field mapping structure
        self.import_mapper = importer(
            disable_reactionpost_ref,
            self.geocode_dict,
            map_relations,
            transfer_reactions,
            ignore_non_geotagged,
            self.ignore_sources_set,
            min_geoaccuracy)
        self.finished = False

    def __enter__(self) -> Iterator[LBSNObjects]:
        """Main pipeline for reading input data

        Combine multiple generators to single pipeline,
        returned for being processed by with-statement
        """
        if self.cursor_input or self.source_web:
            return self.convert_records(self._process_input())
        else:
            return self.convert_records(
                self._process_input(self._open_input_files()))

    def __exit__(self, exception_type, exception_value, tb_value):
        """Contextmanager exit: nothing to do here if no exception is raised"""
        if any(v is not None for v in [
                exception_type, exception_value, tb_value]):
            # only if any of these variables is not None
            # catch exception and output additional information
            logging.getLogger('__main__').warning(
                f"\nError while reading records: "
                f"{exception_type}\n{exception_value}\n"
                f"{traceback.print_tb(tb_value)}\n")
            logging.getLogger('__main__').warning(
                f"Current source: \n {self.current_source}\n")
            stats_str = HF.report_stats(
                self.count_glob,
                self.continue_number)
            logging.getLogger('__main__').warning(stats_str)
        return False

    def _open_input_files(self) -> Iterator[IO[str]]:
        """Loops input filelist and returns opened file handles"""
        # process localfiles
        for file_name in self.filelist:
            self.continue_number += 1
            self.current_source = file_name
            HF.log_main_debug(
                f'Current file: {ntpath.basename(file_name)}')
            yield open(file_name, 'r', encoding="utf-8", errors='replace')

    def _process_input(
            self,
            file_handles: Iterator[IO[str]] = None) -> Iterator[
                Optional[Tuple[List[str], Optional[str]]]]:
        """File parse for CSV or JSON from open file handle

        Output Generator of type Tuple (1, 2):
            1) a list of post that can be parsed
            2) Optional information regarding type of records in list
        """
        if self.source_web:
            if len(self.filelist) == 1:
                # single web file query
                url = self.filelist[0]
                with closing(requests.get(url, stream=True)) as file_handle:
                    record_reader = csv.reader(
                        codecs.iterdecode(
                            file_handle.iter_lines(), 'utf-8'),  # pylint: disable=maybe-no-member
                        delimiter=self.csv_delim,
                        quotechar='"', quoting=csv.QUOTE_NONE)
                    for record in record_reader:
                        # for record in zip_longest(r1, r2)
                        yield record, None
            else:
                # multiple web file query
                if self.zip_records and len(self.filelist) == 2:
                    # zip 2 web csv sources in parallel, e.g.
                    # zip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
                    url1 = self.filelist[0]
                    url2 = self.filelist[1]
                    with closing(requests.get(url1, stream=True)) as fhandle1, \
                            closing(requests.get(url2, stream=True)) as fhandle2:
                        reader1 = csv.reader(
                            codecs.iterdecode(fhandle1.iter_lines(), 'utf-8'),
                            delimiter=self.csv_delim,
                            quotechar='"', quoting=csv.QUOTE_NONE)
                        reader2 = csv.reader(
                            codecs.iterdecode(fhandle2.iter_lines(), 'utf-8'),
                            delimiter=self.csv_delim,
                            quotechar='"', quoting=csv.QUOTE_NONE)
                        for zipped_record in zip_longest(reader1, reader2):
                            # catch any type-error None record
                            # if zipped_record[0] is None:
                            #     yield zipped_record[1]
                            # if zipped_record[1] is None:
                            #     yield zipped_record[0]
                            # two combine lists
                            try:
                                yield zipped_record[0] + zipped_record[1], None
                            except TypeError:
                                sys.exit(f"Stream appears to have broken. "
                                         f"Check connection and continue at "
                                         f"{self.count_glob}")
                    return
                else:
                    raise ValueError(
                        "Iteration of multiple web sources "
                        "is currently not supported.")
        elif self.is_local_input:
            if file_handles is None:
                raise ValueError("Input is empty")
            if self.zip_records:
                if len(self.filelist) == 2:
                    filehandle1 = next(file_handles)
                    filehandle2 = next(file_handles)
                    for zipped_record in zip_longest(
                            self.fetch_record_from_file(filehandle1),
                            self.fetch_record_from_file(filehandle2)):
                        yield zipped_record[0] + zipped_record[1], None
                else:
                    raise ValueError("Zipping only supported for 2 files.")
            else:
                # local file loop
                for file_handle in file_handles:
                    if not self.file_format == 'json':
                        # csv or txt
                        for record in self.fetch_record_from_file(
                                file_handle):
                            if record:
                                yield record, None
                            else:
                                continue
                    else:
                        # json
                        for record in self.fetch_json_data_from_file(
                                file_handle):
                            if record:
                                yield record, None
                            else:
                                continue
        else:
            # db query
            if self.dbformat_input == "lbsn":
                for lbsn_type, schema_name, table_name, key_col in LBSN_SCHEMA:
                    if table_name in self.exclude_lbsn_objects:
                        continue
                    while self.cursor_input:
                        records = self.fetch_json_data_from_lbsn(
                            cursor=self.cursor_input,
                            start_id=self.continue_number,
                            schema_name=schema_name, table_name=table_name,
                            key_col=key_col)
                        if records is None:
                            break
                        for record in records:
                            yield record, lbsn_type
                    # reset start cursor
                    # note: this will disable --startwith_db_rownumber for
                    # any further lbsnobjects
                    self.continue_number = None
            elif self.dbformat_input == "json":
                while self.cursor_input:
                    records = self.fetch_json_data_from_lbsn(
                        cursor=self.cursor_input, start_id=self.continue_number)
                    for record in records:
                        yield record, self.input_lbsn_type

    def convert_records(
        self, records: Iterator[Optional[Tuple[List[str], Optional[str]]]]
    ) -> Iterator[List[LBSNObjects]]:
        """Loops input json or csv records,
        converts to ProtoBuf structure and adds to records_dict

        Returns statistic-counts, modifies (adds results to) import_mapper
        """
        for record in records:
            self.count_glob += 1
            # skip records based on count
            if self.skip_until_record and self.skip_until_record > self.count_glob:
                print(f'Skipping record {self.count_glob}', end='\r')
                continue
            record_type = None
            if self.is_local_input or self.dbformat_input == "lbsn":
                single_record = record[0]
                record_type = record[1]
            else:
                # e.g. dbformat_input == "json"
                self.db_row_number = record[0]
                single_record = record[2]
            if LoadData.skip_empty_or_other(single_record):
                # skip empty or malformed records
                continue
            if self.local_file_type == 'json' or not self.is_local_input:
                # note: db-records always returned as json-dict
                lbsn_records = self.import_mapper.parse_json_record(
                    single_record, record_type)
            elif self.local_file_type in ('txt', 'csv'):
                lbsn_records = self.import_mapper.parse_csv_record(
                    single_record, record_type)
            else:
                sys.exit(f'Format {self.local_file_type} not supportet.')
            # return record as pipe
            if lbsn_records is None:
                continue
            for lbsn_record in lbsn_records:
                yield lbsn_record

    @staticmethod
    def skip_empty_or_other(single_record):
        """Detect  Rate Limiting Notice or empty records
           so they can be skipped.
        """
        skip = False
        if not single_record or \
            (isinstance(single_record, dict) and
             single_record.get('limit')):
            skip = True
        return skip

    def fetch_json_data_from_lbsn(
            self, cursor, start_id=None, get_max=None,
            number_of_records_to_fetch=10000,
            schema_name=None, table_name=None, key_col=None
    ) -> Optional[List[List[str]]]:
        """Fetches records from Postgres DB

        Keyword arguments:
        cursor -- db-cursor
        start_id -- Offset for querying
        get_max -- optional limit for retrieving records
        number_of_records_to_fetch -- how many records should get fetched
        """
        # if transferlimit is below number_of_records_to_fetch, e.g.  10000,
        # retrieve only necessary volume of records
        if get_max:
            number_of_records_to_fetch = min(
                number_of_records_to_fetch, get_max)
        query_sql = InputSQL.LBSN.get_sql(
            schema_name=schema_name, table_name=table_name,
            start_id=start_id,
            number_of_records_to_fetch=number_of_records_to_fetch,
            key_col=key_col)
        cursor.execute(query_sql)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            return None
        # update last returned db_row_number
        if key_col == None:
            self.continue_number = records[-1][0]
            if not self.start_number:
                # first returned db_row_number
                self.start_number = records[0][0]
        else:
            self.continue_number = records[-1].get(key_col)
            if not self.start_number:
                # first returned db_row_number
                self.start_number = records[0].get(key_col)
        return records

    def fetch_record_from_file(self, file_handle):
        """Fetches CSV or JSON data (including stacked json) from file"""
        if self.file_format in ['txt', 'csv']:
            record_reader = self.fetch_csv_data_from_file(
                file_handle)
        else:
            sys.exit(f'Format {self.file_format} not supported.')
        # return record pipeline
        for record in record_reader:
            yield record

    def fetch_json_data_from_file(self, file_handle):
        """Read json entries from file.

        Typical form is [{json1},{json2}], if is_stacked_json is True:
        will process stacked jsons in the form of {json1}{json2}

        If is_line_separated_json is true:
        {json1}
        {json2}
        ...
        """
        # records = []
        # Stacked JSON is a simple file with many concatenated jsons, e.g.
        # {json1}{json2} etc.
        if self.is_stacked_json:
            # note: this requires loading file completely first
            # not streaming optimized yet
            for record in HF.json_read_wrapper(
                    HF.decode_stacked(file_handle.read())):
                yield record
        if self.is_line_separated_json:
            # json's separated by line ending
            for line in file_handle:
                record = HF.json_load_wrapper(line, single=True)
                yield record
        else:
            # normal json nesting, e.g.  {{record1},{record2}}
            records = HF.json_load_wrapper(file_handle)
            if records:
                if isinstance(records, list):
                    for record in records:
                        yield record
                else:
                    record = records
                    yield record
            yield None
            # streaming version:
            # start_pos = 0
            # while True:
            #     try:
            #         record = json.load(file_handle)
            #         yield record
            #         return
            #     except json.JSONDecodeError as e:
            #         file_handle.seek(start_pos)
            #         json_str = file_handle.read(e.pos)
            #         record = json.loads(json_str)
            #         start_pos += e.pos
            #         yield record

    def fetch_csv_data_from_file(self, file_handle):
        """Read csv entries from file (either *.txt or *.csv).

        The actual CSV formatting is not setable in config yet.
        There are many specifics, e.g.
        # QUOTE_NONE is used here because media saved from Flickr
        does not contain any quotes ""
        """
        if self.csv_delim is None:
            self.csv_delim = ','
        # records = []
        record_reader = csv.reader(file_handle, delimiter=self.csv_delim,
                                   quotechar='"', quoting=csv.QUOTE_NONE)
        return record_reader
        #   next(reader, None)  # skip headerline
        #   records = list(reader)
        #   if not records:
        #       return None
        #   return records

    @staticmethod
    def initialize_connection(
            dbuser_output, dbserveraddress_output,
            dbname_output, dbpassword_output, dbserverport_output,
            readonly: bool = True, dict_cursor: Optional[bool] = None):
        """Establishes connection to DB (Postgres)"""

        if dbuser_output:
            connection = DBConnection(
                serveraddress=dbserveraddress_output,
                dbname=dbname_output,
                user=dbuser_output,
                password=dbpassword_output,
                port=dbserverport_output,
                readonly=readonly)
            conn, cursor = connection.connect(dict_cursor)
        else:
            conn = None
            cursor = None
        return conn, cursor

    @staticmethod
    def _read_local_files(input_path=None, recursive_load=None,
                          local_file_type=None, skip_until_file=None):
        """Read Local Files according to config parameters and
        returns list of file-paths
        """
        if recursive_load:
            excludefolderlist = ["01_DataSetHistory",
                                 "02_UserData", "03_ClippedData", "04_MapVis"]
            excludestartswithfile = ["log", "settings", "GridCoordinates"]
            loc_filelist = \
                LoadData.scan_rec(input_path,
                                  file_format=local_file_type,
                                  excludefolderlist=excludefolderlist,
                                  excludestartswithfile=excludestartswithfile)
        else:
            loc_filelist_gen = input_path.glob(f'*.{local_file_type}')
            loc_filelist = []
            for file_path in loc_filelist_gen:
                loc_filelist.append(file_path)
        if skip_until_file:
            print("Implement skip until file")
        input_count = (len(loc_filelist))
        if input_count == 0:
            sys.exit("No location files found.")
        else:
            return loc_filelist

    @staticmethod
    def load_geocodes(geo_config):
        """Loads coordinates-string tuples for geocoding
        text locations (Optional)
        """
        locationsgeocode_dict = GeocodeLocations()
        locationsgeocode_dict.load_geocodelist(geo_config)
        geocode_dict = locationsgeocode_dict.geocode_dict
        return geocode_dict

    @staticmethod
    def load_ignore_sources(list_source=None):
        """Loads list of source types to be ignored"""
        ignore_source_list = set()
        with open(list_source, newline='', encoding='utf8') as file_handle:
            for ignore_source in file_handle:
                ignore_source_list.add(ignore_source.strip())
        return ignore_source_list

    @staticmethod
    def scan_rec(root, subdirlimit=2, file_format="csv",
                 excludefolderlist=None, excludestartswithfile=None):
        """Recursively scan subdir for datafiles"""
        rval = []
        if excludefolderlist is None:
            excludefolderlist = []
        if excludestartswithfile is None:
            excludestartswithfile = []

        def do_scan(start_dir, output, depth=0):
            for file_handle in os.listdir(start_dir):
                file_handle_path = os.path.join(start_dir, file_handle)
                if os.path.isdir(file_handle_path):
                    if depth < subdirlimit:
                        efound = False
                        # check for excludefolders:
                        for entry in excludefolderlist:
                            if entry in file_handle_path:
                                efound = True
                                break
                        if efound is False:
                            do_scan(file_handle_path, output, depth+1)
                else:
                    if file_handle_path.endswith(file_format):
                        efound = False
                        for entry in excludestartswithfile:
                            if ntpath.basename(
                                    file_handle_path).startswith(entry):
                                efound = True
                                break
                        if efound is False:
                            output.append(file_handle_path)
        do_scan(root, rval, 0)
        return rval
