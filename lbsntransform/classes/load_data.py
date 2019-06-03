# -*- coding: utf-8 -*-

"""
Module for loding data from different sources (CSV, DB, JSON etc.).
"""

import sys
import os
import ntpath
import csv
from pathlib import Path
from glob import glob
from json import loads as json_loads, decoder as json_decoder
from .db_connection import DBConnection
from .helper_functions import HelperFunctions as HF
from .helper_functions import GeocodeLocations


class LoadData():
    """
    Class for loding data from different sources (CSV, DB, JSON etc.).
    """

    def __init__(
            self, importer=None, is_local_input=None,
            startwith_db_rownumber=None,
            skip_until_file=None, cursor_input=None, input_path=None,
            recursive_load=None, local_file_type=None,
            endwith_db_rownumber=None, is_stacked_json=None, csv_delim=None,
            input_lbsn_type=None, geocode_locations=None,
            ignore_input_source_list=None, disable_reactionpost_ref=None,
            map_relations=None, transfer_reactions=None,
            ignore_non_geotagged=None, min_geoaccuracy=None):
        self.is_local_input = is_local_input
        self.start_number = None
        if not self.is_local_input:
            # Start Value, Modify to continue from last processing
            self.continue_number = startwith_db_rownumber
            self.start_number = startwith_db_rownumber
        else:
            self.continue_number = skip_until_file
            self.start_number = 1
        if self.is_local_input:
            self.filelist = LoadData._read_local_files(
                input_path=input_path, recursive_load=recursive_load,
                local_file_type=local_file_type,
                skip_until_file=skip_until_file)
            self.cursor_input = cursor_input
        else:
            self.filelist = None
            # self.cursor_input = LoadData.initialize_connection(
            #    cfg)
        self.finished = False
        self.db_row_number = 0
        self.endwith_db_rownumber = endwith_db_rownumber
        self.is_stacked_json = is_stacked_json
        self.local_file_type = local_file_type
        self.csv_delim = csv_delim
        self.file_format = local_file_type
        self.input_lbsn_type = input_lbsn_type
        self.cursor = None
        self.start_id = None
        #self.transferlimit = cfg.transferlimit
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

    def __enter__(self):
        """Main pipeline for reading input data

        Combine multiple generators to single pipeline,
        returned for being processed by with-statement
        """
        record_pipeline = self.convert_records(self._process_input(
            self._open_input_files()))
        return record_pipeline
        # return record_pipeline

    def __exit__(self, c_type, value, traceback):
        """Contextmanager exit: nothing to do here"""
        return False

    def _open_input_files(self, count: bool = None):
        """Loops input input filelist and
        returns opened file handles
        """
        if self.cursor_input:
            return None
        # process localfiles
        for file_name in self.filelist:
            HF.log_main_debug(f'\nCurrent file: {ntpath.basename(file_name)}')
            return open(file_name, 'r', encoding="utf-8", errors='replace')

    def _process_input(self, file_handle):
        """File parse for CSV or JSON from open file handle

        Output: produces a list of post that can be parsed
        """
        if self.is_local_input:
            while file_handle:
                record = self.fetch_record_from_file(
                    file_handle)
                yield record
        else:
            while self.cursor:
                record = self.fetch_json_data_from_lbsn(
                    self.cursor, self.continue_number)
                yield record

    def convert_records(self, record_pipe):
        """Loops input json or csv records,
        converts to ProtoBuf structure and adds to records_dict

        Returns statistic-counts, modifies (adds results to) import_mapper
        """
        for record in record_pipe:
            if self.is_local_input:
                single_record = record
            else:
                self.db_row_number = record[0]
                single_record = record[2]
            # test for empty or malformed records
            if LoadData.skip_empty_or_other(single_record):
                return None
            if self.local_file_type == 'json' or not self.is_local_input:
                # note: db-records always returned as json
                self.import_mapper.parse_json_record(
                    single_record, self.input_lbsn_type)
            elif self.local_file_type in ('txt', 'csv'):
                lbsn_records = self.import_mapper.parse_csv_record(
                    single_record)
            else:
                exit(f'Format {self.local_file_type} not supportet.')
            # return record as pipe
            yield lbsn_records

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

    def fetch_json_data_from_lbsn(self, cursor, start_id=0, get_max=None,
                                  number_of_records_to_fetch=10000):
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
        query_sql = '''
                SELECT in_id,insert_time,data::json FROM public."input"
                WHERE in_id > %s
                ORDER BY in_id ASC LIMIT %s;
                '''
        cursor.execute(query_sql, (start_id, number_of_records_to_fetch))
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            return None
        # update last returned db_row_number
        self.continue_number = records[-1][0]
        if not self.start_number:
            # first returned db_row_number
            self.start_number = records[0][0]
        for record in records:
            return record

    def fetch_record_from_file(self, file_handle):
        """Fetches CSV or JSON data (including stacked json) from file"""

        if self.file_format == 'json':
            record_reader = self.fetch_json_data_from_file(
                file_handle)
        elif self.file_format in ['txt', 'csv']:
            record_reader = self.fetch_csv_data_from_file(
                file_handle)
        else:
            exit(f'Format {self.file_format} not supported.')
        # return record pipeline
        for record in record_reader:
            return record

    def fetch_json_data_from_file(self, file_handle, start_file_id=0):
        """Read json entries from file.

        Typical form is [{json1},{json2}], if is_stacked_json is True:
        will process stacked jsons in the form of {json1}{json2}
        """
        records = []
        # Stacked JSON is a simple file with many concatenated jsons, e.g.
        # {json1}{json2} etc.
        if self.is_stacked_json:
            try:
                for obj in HF.decode_stacked(file_handle.read()):
                    records.append(obj)
            except json_decoder.JSONDecodeError:
                pass
        else:
            # normal json nesting, e.g.  {{record1},{record2}}
            records = json_loads(file_handle.read())
        if records:
            return records
        return None

    def fetch_csv_data_from_file(self, file_handle):
        """Read csv entries from file (either *.txt or *.csv).

        The actual CSV formatting is not setable in config yet.
        There are many specifics, e.g.
        #QUOTE_NONE is used here because media saved from Flickr
        does not contain any quotes ""
        """
        if self.csv_delim is None:
            self.csv_delim = ','
        #records = []
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
            readonly: bool = True):
        """Establishes connection to DB (Postgres)"""

        if dbuser_output:
            connection = DBConnection(
                serveraddress=dbserveraddress_output,
                dbname=dbname_output,
                user=dbuser_output,
                password=dbpassword_output,
                port=dbserverport_output,
                readonly=readonly)
            conn, cursor = connection.connect()
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
            loc_filelist = glob(f'{input_path}*.{local_file_type}')
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
        if list_source is None:
            return
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
