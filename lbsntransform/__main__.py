#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lbsntransform package script to load, format and store data
from and to common lbsn structure

Import options:
    - Postgres Database or
    - local CSV/json/stacked json import
Output options:
    - Postgres Database or
    - local ProtoBuf and CSV Import (prepared for Postgres /Copy)
"""

import logging
import io

__author__ = "Alexander Dunkel"
__license__ = "GNU GPLv3"


def main():
    """ Main function to process data from postgres db or local file input
        to postgres db or local file output
    """
    import sys
    from .classes.helper_functions import TimeMonitor
    from .classes.helper_functions import HelperFunctions as HF
    from .classes.submit_data import LBSNTransfer
    from .classes.load_data import LoadData
    from .config.config import BaseConfig

    # Set Output to Replace in case of encoding issues (console/windows)
    sys.stdout = io.TextIOWrapper(
        sys.stdout.detach(), sys.stdout.encoding, 'replace')
    # Load Config, will be overwritten if args are given
    config = BaseConfig()
    # Parse args
    config.parseArgs()
    sys.stdout.flush()
    log = set_logger()
    # load import mapper depending on lbsn origin (e.g. 1 = Instagram,
    #                                                   2 = Flickr,
    #                                                   3 = Twitter)
    importer = HF.load_importer_mapping_module(config.origin)
    # establish output connection
    conn_output, cursor_output = LoadData.initialize_output_connection(config)
    output = LBSNTransfer(db_cursor=cursor_output,
                          db_connection=conn_output,
                          store_csv=config.csv_output,
                          SUPPRESS_LINEBREAKS=config.csv_suppress_linebreaks)
    # load from local json/csv or from PostgresDB
    if config.is_local_input:
        loc_filelist = LoadData.read_local_files(config)
    else:
        # establish input connection
        cursor_input = LoadData.initialize_input_connection(config)

    # start settings
    processed_records = 0
    processed_total = 0
    start_number = 0
    skipped_low_geoaccuracy = 0
    skipped_low_geoaccuracy_total = 0
    # Start Value, Modify to continue from last processing
    continue_number = config.startwith_db_rownumber

    # Optional Geocoding
    geocode_dict = False
    if config.geocode_locations:
        geocode_dict = LoadData.load_geocodes(config.geocode_locations)
    # Optional ignore input sources
    ignore_sources_set = None
    if config.ignore_input_source_list:
        ignore_sources_set = LoadData.load_ignore_sources(
            config.ignore_input_source_list)

    finished = False
    # initialize field mapping structure
    import_mapper = importer(config.disable_reactionpost_ref,
                             geocode_dict,
                             config.map_relations,
                             config.transfer_reactions,
                             config.ignore_non_geotagged,
                             ignore_sources_set,
                             config.min_geoaccuracy)
    # Manually add entries that need submission prior to parsing data
    # add_bundestag_group_example(import_mapper)

    how_long = TimeMonitor()
    # loop input DB until transferlimit reached or no more rows are returned
    while not finished:
        if config.transferlimit:
            max_records = config.transferlimit - processed_total
        else:
            max_records = None
        if config.is_local_input:
            if continue_number > len(loc_filelist) - 1:
                break
            records = LoadData.fetch_data_from_file(loc_filelist,
                                                    continue_number,
                                                    config.is_stacked_json,
                                                    config.local_file_type)
            # skip empty files
            if not records:
                continue_number += 1
                continue
        else:
            records = \
                LoadData.fetch_json_data_from_lbsn(
                    cursor_input,
                    continue_number,
                    max_records,
                    config.number_of_records_to_fetch)
            if not records:
                break
        if config.is_local_input:
            continue_number += 1
        else:
            continue_number = records[-1][0]  # last returned db_row_number
        processed_count, finished = \
            LoadData.loop_input_records(
                records,
                max_records,
                import_mapper,
                config)
        processed_records += processed_count
        processed_total += processed_count
        skipped_low_geoaccuracy_total += import_mapper.skipped_low_geoaccuracy
        print(f'{processed_total} input records processed (up to '
              f'{continue_number}). '
              f'Skipped {skipped_low_geoaccuracy} due to low geoaccuracy. '
              f'Count per type: {import_mapper.lbsn_records.get_type_counts()}'
              f'records.', end='\n')

        # update console
        # On the first loop or after 500.000 processed records,
        # transfer results to DB
        if not start_number or processed_records >= config.transfer_count or \
                finished:
            sys.stdout.flush()
            print(f'Storing {import_mapper.lbsn_records.count_glob} records.. '
                  f'{HF.null_notice(import_mapper.null_island)})')
            output.store_lbsn_record_dicts(import_mapper)
            output.commit_changes()
            processed_records = 0
            # create a new empty dict of records
            import_mapper = importer(config.disable_reactionpost_ref,
                                     geocode_dict,
                                     config.map_relations,
                                     config.transfer_reactions,
                                     config.ignore_non_geotagged,
                                     ignore_sources_set,
                                     config.min_geoaccuracy)
        # remember the first processed DBRow ID
        if not start_number:
            if config.is_local_input:
                start_number = 1
            else:
                start_number = records[0][0]  # first returned db_row_number

    # submit remaining
    # ??
    if import_mapper.lbsn_records.count_glob > 0:
        print(f'Transferring remaining '
              f'{import_mapper.lbsn_records.count_glob} to db.. '
              f'{HF.null_notice(import_mapper.null_island)})')
        output.store_lbsn_record_dicts(import_mapper)
        output.commit_changes()

    # finalize all transactions (csv merge etc.)
    output.finalize()

    # Close connections to DBs
    if not config.is_local_input:
        cursor_input.close()
    if config.dbuser_output:
        cursor_output.close()
    log.info(f'\n\nProcessed {processed_total} input records '
             f'(Input {start_number} to {continue_number}).'
             f'Skipped {skipped_low_geoaccuracy_total} '
             f'due to low geoaccuracy.')
    input(f'Done. {how_long.stop_time()}')


def set_logger():
    """ Set logging handler manually,
    so we can also print to console while logging to file
    """

    logging.basicConfig(
        handlers=[logging.FileHandler(
            'log.log', 'w', 'utf-8')],
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    log = logging.getLogger(__name__)
    # Get Stream handler
    logging.getLogger().addHandler(logging.StreamHandler())
    return log


if __name__ == "__main__":
    main()
