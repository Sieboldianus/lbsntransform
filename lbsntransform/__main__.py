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

import sys

from lbsntransform.tools.helper_functions import HelperFunctions as HF
from lbsntransform.output.shared_structure import TimeMonitor
from lbsntransform.input.load_data import LoadData
from lbsntransform.config.config import BaseConfig
from lbsntransform.lbsntransform_ import LBSNTransform


def main():
    """ Main function for cli-mode to process data
    from postgres db or local file input
    to postgres db or local file output
    """

    # Load Config, will be overwritten if args are given
    config = BaseConfig()
    # Parse args
    config.parse_args()

    # initialize lbsntransform
    lbsntransform = LBSNTransform(
        origin_id=config.origin,
        logging_level=config.logging_level,
        is_local_input=config.is_local_input,
        transfer_count=config.transfer_count,
        csv_output=config.csv_output,
        csv_suppress_linebreaks=config.csv_suppress_linebreaks,
        dbuser_output=config.dbuser_output,
        dbserveraddress_output=config.dbserveraddress_output,
        dbname_output=config.dbname_output,
        dbpassword_output=config.dbpassword_output,
        dbserverport_output=config.dbserverport_output,
        dbformat_output=config.dbformat_output,
        dbuser_input=config.dbuser_input,
        dbserveraddress_input=config.dbserveraddress_input,
        dbname_input=config.dbname_input,
        dbpassword_input=config.dbpassword_input,
        dbserverport_input=config.dbserverport_input,
        dbuser_hllworker=config.dbuser_hllworker,
        dbserveraddress_hllworker=config.dbserveraddress_hllworker,
        dbname_hllworker=config.dbname_hllworker,
        dbpassword_hllworker=config.dbpassword_hllworker,
        dbserverport_hllworker=config.dbserverport_hllworker,
        include_lbsn_bases=config.include_lbsn_bases)

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
        is_line_separated_json=config.is_line_separated_json,
        csv_delim=config.csv_delim,
        input_lbsn_type=config.input_lbsn_type,
        dbformat_input=config.dbformat_input,
        geocode_locations=config.geocode_locations,
        ignore_input_source_list=config.ignore_input_source_list,
        disable_reactionpost_ref=config.disable_reactionpost_ref,
        map_relations=config.map_relations,
        transfer_reactions=config.transfer_reactions,
        ignore_non_geotagged=config.ignore_non_geotagged,
        min_geoaccuracy=config.min_geoaccuracy,
        source_web=config.source_web,
        skip_until_record=config.skip_until_record,
        zip_records=config.zip_records,
        exclude_lbsn_objects=config.exclude_lbsn_objects)

    # Manually add entries that need submission prior to parsing data
    # add_bundestag_group_example(import_mapper)

    # init time monitoring
    how_long = TimeMonitor()

    # read and process unfiltered input records from csv
    # start settings
    with input_data as records:
        for record in records:
            lbsntransform.add_processed_records(record)
            # report progress
            if lbsntransform.processed_total % 1000 == 0:
                stats_str = HF.report_stats(
                    input_data.count_glob,
                    input_data.continue_number,
                    lbsntransform.lbsn_records)
                print(stats_str, end='\r')
                sys.stdout.flush()
            if (config.transferlimit and
                    lbsntransform.processed_total >= config.transferlimit):
                break

    # finalize output (close db connection, submit remaining)
    lbsntransform.log.info(
        f'\nTransferring remaining '
        f'{lbsntransform.lbsn_records.count_glob} to db.. '
        f'{HF.null_notice(input_data.import_mapper.null_island)})')
    lbsntransform.finalize_output()

    # final report
    lbsntransform.log.info(
        f'\n\nProcessed {input_data.count_glob} input records '
        f'(Input {input_data.start_number} to '
        f'{input_data.continue_number}). '
        f'\n\nIdentified {lbsntransform.processed_total} LBSN records, '
        f'with {lbsntransform.lbsn_records.count_glob_total} '
        f'distinct LBSN records overall. '
        f'{HF.get_skipped_report(input_data.import_mapper)}. '
        f'Merged {lbsntransform.lbsn_records.count_dup_merge_total} '
        f'duplicate records.')
    lbsntransform.log.info(
        f'\n{HF.get_count_stats(lbsntransform.lbsn_records)}')

    lbsntransform.log.info(f'Done. {how_long.stop_time()}')

    lbsntransform.close_log()


if __name__ == "__main__":
    main()
