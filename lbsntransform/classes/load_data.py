# -*- coding: utf-8 -*-
from .db_connection import DBConnection
from .helper_functions import HelperFunctions
from glob import glob
#import json
from json import loads as json_loads, decoder as json_decoder
#from json import decoder, JSONDecoder, JSONDecodeError

class LoadData():
    def loop_input_records(json_records, transferlimit, twitter_records, end_with_db_row_number, is_local_input, input_type):
        """Loops input json records, converts to ProtoBuf structure and adds to records_dict

        Returns statistic-counts, modifies twitter_records
        """

        finished = False
        processed_records = 0
        db_row_number = 0
        for record in json_records:
            processed_records += 1
            if is_local_input:
                single_json_record_dict = record
            else:
                db_row_number = record[0]
                single_json_record_dict = record[2]
            if not single_json_record_dict or single_json_record_dict.get('limit'):
                # Skip Rate Limiting Notice or empty records
                continue
            twitter_records.parseJsonRecord(single_json_record_dict, input_type)
            if (transferlimit and processed_records >= transferlimit) or \
               (not is_local_input and end_with_db_row_number and db_row_number >= end_with_db_row_number):
                finished = True
                break
        return processed_records, finished

    ## edit the following procedures to your structure

    def fetch_json_data_from_lbsn(cursor, start_id=0, get_max=None, number_of_records_to_fetch=10000):
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
            number_of_records_to_fetch = min(number_of_records_to_fetch, get_max)
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

    def fetch_json_data_from_file(loc_filelist, start_file_id=0, is_stacked_json=False):
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
                    for obj in HelperFunctions.decode_stacked(file.read()):
                        records.append(obj)
                except json_decoder.JSONDecodeError:
                    pass
            else:
                # normal json nesting, e.g.  {{record1},{record2}}
                records = json_loads(file.read())
        if records:
            return records
        return None

    def add_bundestag_group_example(twitter_records):
        """ Example: Manually add Group that applies to all entries.
            To use, must uncomment fieldMapping/extractUser
        """

        deutscher_bundestag_group = helperFunctions.createNewLBSNRecord_with_id(lbsnUserGroup(), "MdB (Bundestag)", twitter_records.origin)
        dbg_owner = helperFunctions.createNewLBSNRecord_with_id(lbsnUser(), "243586130", twitter_records.origin)
        dbg_owner.user_name = 'wahl_beobachter'
        dbg_owner.user_fullname = 'Martin Fuchs'
        deutscher_bundestag_group.user_owner_pkey.CopyFrom(dbg_owner.pkey)
        deutscher_bundestag_group.usergroup_description = 'Alle twitternden Abgeordneten aus dem Deutschen Bundestag #bundestag'
        twitter_records.lbsnRecords.AddRecordToDict(dbg_owner)
        twitter_records.lbsnRecords.AddRecordToDict(deutscher_bundestag_group)

    def initialize_output_connection(config):
        """Establishes connection to output DB (Postgres), if set in config"""
        if config.dbUser_Output:
            output_connection = DBConnection(config.dbServeradressOutput,
                                             config.dbNameOutput,
                                             config.dbUser_Output,
                                             config.dbPassword_Output)
            conn_output, cursor_output = output_connection.connect()
        else:
            conn_output = None
            cursor_output = None
        return conn_output, cursor_output

    def initialize_input_connection(config):
        """Establishes connection to input DB (Postgres)

        Returns cursor
        """
        input_connection = DBConnection(config.dbServeradressInput,
                                        config.dbNameInput,
                                        config.dbUser_Input,
                                        config.dbPassword_Input,
                                        True # ReadOnly Mode
                                        )
        conn_input, cursor_input = input_connection.connect()
        return cursor_input

    def read_local_files(config):
        """Read Local Files according to config parameters and returns list of file-paths"""
        filepath = f'{config.InputPath}{config.LocalFileType}'
        loc_filelist = glob(filepath)
        input_count = (len(loc_filelist))
        if input_count == 0:
            sys.exit("No location files found.")
        else:
            return loc_filelist

    def load_geocodes(geo_config):
        """Loads coordinates-string tuples for geocoding text locations (Optional)"""
        locationsgeocode_dict = geocodeLocations()
        locationsgeocode_dict.load_geocodelist(geo_config)
        geocode_dict = locationsgeocode_dict.geocode_dict
        return geocode_dict
