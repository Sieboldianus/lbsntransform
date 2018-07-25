#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Collection of classes to import, convert and export data
from and to common lbsn structure

Import options:
    - Postgres Database or
    - local CSV/json/stacked json import
Output options:
    - Postgres Database or
    - local ProtoBuf and CSV Import (prepared for Postgres /Copy)

For more info, see [concept](https://gitlab.vgiscience.de/lbsn/concept)
"""

__author__ = "Alexander Dunkel"
__license__ = "GNU GPLv3"
__version__ = "0.1.4"

import logging
import io
import sys
# Only necessary for local import/export:
from glob import glob
import json
# import ppygis3 # PostGIS geometry objects in python
# LBSN Structure Import from ProtoBuf (vendor directory)
from classes.dbConnection import dbConnection
from classes.helperFunctions import helperFunctions
###from transfer_lbsn_data.classes.helperFunctions import lbsnRecordDicts
from classes.helperFunctions import geocodeLocations
from classes.helperFunctions import timeMonitor
from classes.fieldMapping import fieldMappingTwitter
from classes.submitData import lbsnDB
#import config.config

from config.config import baseconfig

def main():
    """ Example function to process data from postgres connection or local file input"""


    # Set Output to Replace in case of encoding issues (console/windows)
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), sys.stdout.encoding, 'replace')
    # Load Config, will be overwritten if args are given
    config = baseconfig()
    # Parse args
    config.parseArgs()
    sys.stdout.flush()
    log = set_logger()
    # establish output connection (will return none of no config)
    conn_output, cursor_output = initialize_output_connection(config)
    output = lbsnDB(dbCursor=cursor_output,
                    dbConnection=conn_output,
                    storeCSV=config.CSVOutput,
                    CSVsuppressLinebreaks=config.CSVsuppressLinebreaks)
    # load from local json/csv or from PostgresDB
    if config.LocalInput:
        loc_filelist = read_local_files(config)
    else:
        # establish input connection
        cursor_input = initialize_input_connection(config)

    # start settings
    processed_records = 0
    processed_total = 0
    start_number = 0
    # Start Value, Modify to continue from last processing
    continue_number = config.startWithdb_row_number

    # Optional Geocoding
    geocode_dict = False
    if config.geocodeLocations:
        geocode_dict = load_geocodes(config.geocodeLocations)

    finished = False
    # initialize field mapping structure
    twitter_records = fieldMappingTwitter(config.disableReactionPostReferencing,
                                          geocode_dict,
                                          config.MapRelations)

    # Manually add entries that need submission prior to parsing data
    # add_bundestag_group_example(twitter_records)

    how_long = timeMonitor()
    # loop input DB until transferlimit reached or no more rows are returned
    while not finished:
        if config.transferlimit:
            max_records = config.transferlimit - processed_total
        else:
            max_records = None
        if config.LocalInput:
            if continue_number > len(loc_filelist) - 1:
                break
            records = fetch_json_data_from_file(loc_filelist,
                                                continue_number,
                                                config.is_stacked_json)
            # skip empty files
            if not records:
                continue_number += 1
                continue
        else:
            records = fetch_json_data_from_lbsn(cursor_input,
                                                continue_number,
                                                max_records,
                                                config.number_of_records_to_fetch)
            if not records:
                break
        if config.LocalInput:
            continue_number += 1
        else:
            continue_number = records[-1][0] #last returned db_row_number
        processed_count, finished = loop_input_records(records,
                                                       max_records,
                                                       twitter_records,
                                                       config.end_with_db_row_number,
                                                       config.LocalInput,
                                                       config.input_type)
        processed_records += processed_count
        processed_total += processed_count
        print(f'{processed_total} input records processed (up to {continue_number}). '
              'Count per type: {twitter_records.lbsnRecords.getTypeCounts()}records.', end='\n')
        # update console
        # On the first loop or after 500.000 processed records, transfer results to DB
        if not start_number or processed_records >= config.transferCount or finished:
            sys.stdout.flush()
            print(f'Storing {twitter_records.lbsnRecords.CountGlob} records ..')
            output.storeLbsnRecordDicts(twitter_records)
            output.commitChanges()
            processed_records = 0
            ## create a new empty dict of records
            twitter_records = fieldMappingTwitter(config.disableReactionPostReferencing,
                                                  geocode_dict,
                                                  config.MapRelations)
        # remember the first processed DBRow ID
        if not start_number:
            if config.LocalInput:
                start_number = 1
            else:
                start_number = records[0][0] #first returned db_row_number

    # submit remaining
    # ??
    if twitter_records.lbsnRecords.CountGlob > 0:
        print(f'Transferring remaining {twitter_records.lbsnRecords.CountGlob} to db..')
        output.storeLbsnRecordDicts(twitter_records)
        output.commitChanges()

    if config.CSVOutput:
        # merge all CSVs at end and remove duplicates
        # this is necessary because Postgres can't import Duplicates with /copy
        # and it is impossible to keep all records in RAM while processing input data
        output.cleanCSVBatches()

    # Close connections to DBs
    if not config.LocalInput:
        cursor_input.close()
    if config.dbUser_Output:
        cursor_output.close()
    log.info(f'\n\nProcessed {processed_total} input records '
             '(Input {start_number} to {continue_number}).')
    input(f'Done. {how_long.stop_time()}')

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
    # if transferlimit is below number_of_records_to_fetch, e.g. 10000,
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
        # Stacked JSON is a simple file with many concatenated jsons, e.g. {json1}{json2} etc.
        if is_stacked_json:
            try:
                for obj in helperFunctions.decode_stacked(file.read()):
                    records.append(obj)
            except json.decoder.JSONDecodeError:
                pass
        else:
            # normal json nesting, e.g. {{record1},{record2}}
            records = json.loads(file.read())
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

def set_logger():
    """ Set logging handler manually, so we can also print to console while logging to file"""

    logging.basicConfig(handlers=[logging.FileHandler('log.log', 'w', 'utf-8')],
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    log = logging.getLogger(__name__)
    # Get Stream handler
    logging.getLogger().addHandler(logging.StreamHandler())
    return log

def initialize_output_connection(config):
    """Establishes connection to output DB (Postgres), if set in config"""
    if config.dbUser_Output:
        output_connection = dbConnection(config.dbServeradressOutput,
                                        config.dbNameOutput,
                                        config.dbUser_Output,
                                        config.dbPassword_Output
                                        )
        conn_output, cursor_output = output_connection.connect()
    else:
        conn_output = None
        cursor_output = None
    return conn_output, cursor_output

def initialize_input_connection(config):
    """Establishes connection to input DB (Postgres)

    Returns cursor
    """
    input_connection = dbConnection(config.dbServeradressInput,
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

if __name__ == "__main__":
    main()
