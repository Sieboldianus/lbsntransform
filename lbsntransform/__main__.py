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

__author__ = "Alexander Dunkel"
__license__ = "GNU GPLv3"
# version: see version.py

import io
import logging
import sys

from lbsntransform.lbsntransform_ import LBSNTransform
from lbsntransform.classes.helper_functions import HelperFunctions as HF
from lbsntransform.classes.helper_functions import TimeMonitor
from lbsntransform.classes.load_data import LoadData
from lbsntransform.classes.submit_data import LBSNTransfer
from lbsntransform.config.config import BaseConfig


def main():
    """ Main function to process data from postgres db or local file input
        to postgres db or local file output
    """

    # Load Config, will be overwritten if args are given
    config = BaseConfig()
    # Parse args
    config.parseArgs()

    # initialize lbsntransform
    lbsntransform = LBSNTransform(
        origin=config.origin,
        logging_level=config.logging_level,
        is_local_input=config.is_local_input,
        csv_output=config.csv_output,
        csv_suppress_linebreaks=config.csv_suppress_linebreaks,
        dbuser_output=config.dbuser_output,
        dbserveraddress_output=config.dbserveraddress_output,
        dbname_output=config.dbname_output,
        dbpassword_output=config.dbpassword_output,
        dbserverport_output=config.dbserverport_output,
        dbuser_input=config.dbuser_input,
        dbserveraddress_input=config.dbserveraddress_input,
        dbname_input=config.dbname_input,
        dbpassword_input=config.dbpassword_input,
        dbserverport_input=config.dbserverport_input)

    # initialize converter class
    # depending on lbsn origin
    # e.g. 1 = Instagram,
    #      2 = Flickr, 2.1 = Flickr YFCC100m,
    #      3 = Twitter)
    importer = HF.load_importer_mapping_module(
        config.origin)

    # initialize input reader
    input_data = LoadData(
        importer=importer,
        is_local_input=config.is_local_input,
        startwith_db_rownumber=config.startwith_db_rownumber,
        skip_until_file=config.skip_until_file,
        cursor_input=lbsntransform.cursor_input,
        input_path=config.input_path,
        recursive_load=config.recursive_load,
        local_file_type=config.local_file_type,
        endwith_db_rownumber=config.endwith_db_rownumber,
        is_stacked_json=config.is_stacked_json,
        csv_delim=config.csv_delim,
        input_lbsn_type=config.input_lbsn_type,
        geocode_locations=config.geocode_locations,
        ignore_input_source_list=config.ignore_input_source_list,
        disable_reactionpost_ref=config.disable_reactionpost_ref,
        map_relations=config.map_relations,
        transfer_reactions=config.transfer_reactions,
        ignore_non_geotagged=config.ignore_non_geotagged,
        min_geoaccuracy=config.min_geoaccuracy)

    # Manually add entries that need submission prior to parsing data
    # add_bundestag_group_example(import_mapper)

    # init time monitoring
    how_long = TimeMonitor()

    # read and process unfiltered input records from csv
    # start settings
    with input_data as records_list:
        for lbsn_record in records_list:
            lbsntransform.add_processed_records(lbsn_record)
            # report progress
            if lbsntransform.processed_total % 1000 == 0:
                print(
                    f'{lbsntransform.processed_total} '
                    f'input records processed (up to '
                    f'{input_data.continue_number}). '
                    f'Skipped '
                    f'{input_data.import_mapper.skipped_low_geoaccuracy} '
                    f'due to low geoaccuracy. '
                    f'Count per type: '
                    f'{lbsntransform.lbsn_records.get_type_counts()}'
                    f'records.', end='\r')

    # finalize output (close db connection, submit remaining)
    print(f'Transferring remaining '
          f'{lbsntransform.lbsn_records.count_glob} to db.. '
          f'{HF.null_notice(input_data.import_mapper.null_island)})')
    lbsntransform.finalize_output()

    # final report
    print(f'\n\nProcessed {lbsntransform.processed_total} input records '
          f'(Input {lbsntransform.start_number} to '
          f'{lbsntransform.continue_number}). '
          f'Skipped {input_data.import_mapper.skipped_low_geoaccuracy} '
          f'due to low geoaccuracy.')

    input(f'Done. {how_long.stop_time()}')

    # loop input DB until transferlimit reached or no more rows are returned
    # while not finished:
    #     if config.transferlimit:
    #         max_records = config.transferlimit - processed_total
    #     else:
    #         max_records = None
    #     if config.is_local_input:
    #         if continue_number > len(loc_filelist) - 1:
    #             break
    #         records = LoadData.fetch_data_from_file(
    #             loc_filelist,
    #             continue_number,
    #             config.is_stacked_json,
    #             config.local_file_type,
    #             config.csv_delim)
    #         # skip empty files
    #         if not records:
    #             continue_number += 1
    #             continue
    #     else:
    #         records = \
    #             LoadData.fetch_json_data_from_lbsn(
    #                 cursor_input,
    #                 continue_number,
    #                 max_records,
    #                 config.number_of_records_to_fetch)
    #         if not records:
    #             break
    #     if config.is_local_input:
    #         continue_number += 1
    #     else:
    #         continue_number = records[-1][0]  # last returned db_row_number
    #     processed_count, finished = \
    #         LoadData.loop_input_records(
    #             records,
    #             max_records,
    #             import_mapper,
    #             config)
    #     processed_records += processed_count
    #     processed_total += processed_count
    #     skipped_low_geoaccuracy_total += import_mapper.skipped_low_geoaccuracy
    #     print(f'{processed_total} input records processed (up to '
    #           f'{continue_number}). '
    #           f'Skipped {skipped_low_geoaccuracy} due to low geoaccuracy. '
    #           f'Count per type: {import_mapper.lbsn_records.get_type_counts()}'
    #           f'records.', end='\n')
#
    #     # update console
    #     # On the first loop or after 500.000 processed records,
    #     # transfer results to DB
    #     if not start_number or processed_records >= config.transfer_count or \
    #             finished:
    #         sys.stdout.flush()
    #         print(f'Storing {import_mapper.lbsn_records.count_glob} records.. '
    #               f'{HF.null_notice(import_mapper.null_island)})')
    #         output.store_lbsn_record_dicts(import_mapper)
    #         output.commit_changes()
    #         processed_records = 0
    #         # create a new empty dict of records
    #         import_mapper = importer(config.disable_reactionpost_ref,
    #                                  geocode_dict,
    #                                  config.map_relations,
    #                                  config.transfer_reactions,
    #                                  config.ignore_non_geotagged,
    #                                  ignore_sources_set,
    #                                  config.min_geoaccuracy)
    #     # remember the first processed DBRow ID
    #     if not start_number:
    #         if config.is_local_input:
    #             start_number = 1
    #         else:
    #             start_number = records[0][0]  # first returned db_row_number

    # submit remaining
    # ??
    # if import_mapper.lbsn_records.count_glob > 0:
    #    print(f'Transferring remaining '
    #          f'{import_mapper.lbsn_records.count_glob} to db.. '
    #          f'{HF.null_notice(import_mapper.null_island)})')
    #    output.store_lbsn_record_dicts(import_mapper)
    #    output.commit_changes()

    # finalize all transactions (csv merge etc.)
    # output.finalize()

    # Close connections to DBs
    # if not config.is_local_input:
    #     cursor_input.close()
    # if config.dbuser_output:
    #     cursor_output.close()
    # log.info(f'\n\nProcessed {processed_total} input records '
    #         f'(Input {start_number} to {continue_number}). '
    #         f'Skipped {skipped_low_geoaccuracy_total} '
    #         f'due to low geoaccuracy.')
    # input(f'Done. {how_long.stop_time()}')


if __name__ == "__main__":
    main()
