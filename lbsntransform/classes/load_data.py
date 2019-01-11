# -*- coding: utf-8 -*-

"""
Module for loding data from different sources (CSV, DB, JSON etc.).
"""

import sys
import os
import ntpath
import csv
from glob import glob
from json import loads as json_loads, decoder as json_decoder
from .db_connection import DBConnection
from .helper_functions import HelperFunctions as HF
from .helper_functions import GeocodeLocations


class LoadData():
    """
    Class for loding data from different sources (CSV, DB, JSON etc.).
    """
    @staticmethod
    def loop_input_records(records, transferlimit, import_mapper, config):
        """Loops input json or csv records,
        converts to ProtoBuf structure and adds to records_dict

        Returns statistic-counts, modifies (adds results to) import_mapper
        """

        finished = False
        processed_records = 0
        db_row_number = 0
        for record in records:
            processed_records += 1
            if config.is_local_input:
                single_record = record
            else:
                db_row_number = record[0]
                single_record = record[2]
            if LoadData.skip_empty_or_other(single_record):
                continue
            if config.local_file_type == 'json' or not config.is_local_input:
                import_mapper.parse_json_record(
                    single_record, config.input_lbsn_type)
            elif config.local_file_type in ('txt', 'csv'):
                import_mapper.parse_csv_record(single_record)
            else:
                exit(f'Format {config.local_file_type} not supportet.')

            if (transferlimit and processed_records >= transferlimit) or \
               (not config.is_local_input and
                config.endwith_db_rownumber and
                    db_row_number >= config.endwith_db_rownumber):
                finished = True
                break
        return processed_records, finished

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

    @staticmethod
    def fetch_json_data_from_lbsn(cursor, start_id=0, get_max=None,
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
        return records

    @staticmethod
    def fetch_data_from_file(loc_filelist, continue_number,
                             is_stacked_json, file_format):
        """Fetches CSV or JSON data (including stacked json) from file"""
        if file_format == 'json':
            records = LoadData.fetch_json_data_from_file(loc_filelist,
                                                         continue_number,
                                                         is_stacked_json)
        elif file_format == 'txt':
            records = LoadData.fetch_csv_data_from_file(loc_filelist,
                                                        continue_number)
        else:
            exit(f'Format {file_format} not supported.')
        return records

    @staticmethod
    def fetch_json_data_from_file(loc_filelist, start_file_id=0,
                                  is_stacked_json=False):
        """Read json entries from file.

        Typical form is [{json1},{json2}], if is_stacked_json is True:
        will process stacked jsons in the form of {json1}{json2}
        """
        records = []
        loc_file = loc_filelist[start_file_id]
        with open(loc_file, 'r', encoding="utf-8", errors='replace') as file:
            # Stacked JSON is a simple file with many concatenated jsons, e.g.
            # {json1}{json2} etc.
            if is_stacked_json:
                try:
                    for obj in HF.decode_stacked(file.read()):
                        records.append(obj)
                except json_decoder.JSONDecodeError:
                    pass
            else:
                # normal json nesting, e.g.  {{record1},{record2}}
                records = json_loads(file.read())
        if records:
            return records
        return None

    @staticmethod
    def fetch_csv_data_from_file(loc_filelist, start_file_id=0):
        """Read csv entries from file (either *.txt or *.csv).

        The actual CSV formatting is not setable in config yet.
        There are many specifics, e.g.
        #QUOTE_NONE is used here because media saved from Flickr
        does not contain any quotes ""
        """
        records = []
        loc_file = loc_filelist[start_file_id]
        HF.log_main_debug(f'\nCurrent file: {ntpath.basename(loc_file)}')
        with open(loc_file, 'r', encoding="utf-8", errors='replace') as file:
            reader = csv.reader(file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_NONE)
            next(reader, None)  # skip headerline
            records = list(reader)
        if not records:
            return None
        return records

    @staticmethod
    def initialize_output_connection(cfg):
        """Establishes connection to output DB (Postgres), if set in config"""
        if cfg.dbuser_output:
            output_connection = DBConnection(cfg.dbserveradress_output,
                                             cfg.dbname_output,
                                             cfg.dbuser_output,
                                             cfg.dbpassword_output)
            conn_output, cursor_output = output_connection.connect()
        else:
            conn_output = None
            cursor_output = None
        return conn_output, cursor_output

    @staticmethod
    def initialize_input_connection(cfg):
        """Establishes connection to input DB (Postgres)

        Returns cursor
        """
        input_connection = DBConnection(cfg.dbserveradress_input,
                                        cfg.db_name_input,
                                        cfg.dbuser_Input,
                                        cfg.dbpassword_input,
                                        True  # ReadOnly Mode
                                        )
        conn_input, cursor_input = input_connection.connect()
        return cursor_input

    @staticmethod
    def read_local_files(cfg):
        """Read Local Files according to config parameters and
        returns list of file-paths
        """
        path = f'{config.InputPath}'
        if cfg.recursive_load:
            excludefolderlist = ["01_DataSetHistory",
                                 "02_UserData", "03_ClippedData", "04_MapVis"]
            excludestartswithfile = ["log", "settings", "GridCoordinates"]
            loc_filelist = \
                LoadData.scan_rec(path,
                                  file_format=cfg.local_file_type,
                                  excludefolderlist=excludefolderlist,
                                  excludestartswithfile=excludestartswithfile)
        else:
            loc_filelist = glob(f'{path}*.{cfg.local_file_type}')

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
