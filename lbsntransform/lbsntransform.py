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

# temporarily add root path of package to path, so we can execute package directly in development
#sys.path.insert(0, os.path.dirname(__file__))
# Only necessary for local import/export:
from glob import glob
import json

# import ppygis3 # PostGIS geometry objects in python
# LBSN Structure Import from ProtoBuf (vendor directory)


def main():
    """ Example function to process data from postgres connection or local file input"""
    try:
        from .classes.dbConnection import dbConnection
        from .classes.helperFunctions import helperFunctions
        from .classes.helperFunctions import lbsnRecordDicts
        from .classes.helperFunctions import geocodeLocations
        from .classes.helperFunctions import timeMonitor
        from .classes.fieldMapping import fieldMappingTwitter
        from .classes.submitData import lbsnDB
        from .classes.loadData import loadData
        from .config.config import baseconfig
    except ImportError:
        from classes.dbConnection import dbConnection
        from classes.helperFunctions import helperFunctions
        from classes.helperFunctions import lbsnRecordDicts
        from classes.helperFunctions import geocodeLocations
        from classes.helperFunctions import timeMonitor
        from classes.fieldMapping import fieldMappingTwitter
        from classes.submitData import lbsnDB
        from classes.loadData import loadData
        from config.config import baseconfig

    import sys, os

    # Set Output to Replace in case of encoding issues (console/windows)
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), sys.stdout.encoding, 'replace')
    # Load Config, will be overwritten if args are given
    config = baseconfig()
    # Parse args
    config.parseArgs()
    sys.stdout.flush()
    log = set_logger()
    # establish output connection (will return none of no config)
    conn_output, cursor_output = loadData.initialize_output_connection(config)
    output = lbsnDB(dbCursor=cursor_output,
                    dbConnection=conn_output,
                    storeCSV=config.CSVOutput,
                    CSVsuppressLinebreaks=config.CSVsuppressLinebreaks)
    # load from local json/csv or from PostgresDB
    if config.LocalInput:
        loc_filelist = loadData.read_local_files(config)
    else:
        # establish input connection
        cursor_input = loadData.initialize_input_connection(config)

    # start settings
    processed_records = 0
    processed_total = 0
    start_number = 0
    # Start Value, Modify to continue from last processing
    continue_number = config.startWithdb_row_number

    # Optional Geocoding
    geocode_dict = False
    if config.geocodeLocations:
        geocode_dict = loadData.load_geocodes(config.geocodeLocations)

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
            records = loadData.fetch_json_data_from_file(loc_filelist,
                                                         continue_number,
                                                         config.is_stacked_json)
            # skip empty files
            if not records:
                continue_number += 1
                continue
        else:
            records = loadData.fetch_json_data_from_lbsn(cursor_input,
                                                continue_number,
                                                max_records,
                                                config.number_of_records_to_fetch)
            if not records:
                break
        if config.LocalInput:
            continue_number += 1
        else:
            continue_number = records[-1][0] #last returned db_row_number
        processed_count, finished = loadData.loop_input_records(records,
                                                       max_records,
                                                       twitter_records,
                                                       config.end_with_db_row_number,
                                                       config.LocalInput,
                                                       config.input_type)
        processed_records += processed_count
        processed_total += processed_count
        print(f'{processed_total} input records processed (up to {continue_number}). '
              f'Count per type: {twitter_records.lbsnRecords.getTypeCounts()}records.', end='\n')
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
             f'(Input {start_number} to {continue_number}).')
    input(f'Done. {how_long.stop_time()}')

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

if __name__ == "__main__":
    main()
