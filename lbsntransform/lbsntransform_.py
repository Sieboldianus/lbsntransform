# -*- coding: utf-8 -*-

"""
LBSNTransform: Convert Raw Social Media data
         to common LBSN interchange format (ProtoBuf) and
         transfer to local CSV or LBSN Postgres Database
"""

from __future__ import absolute_import

__author__ = "Alexander Dunkel"
__license__ = "GNU GPLv3"

import io
import logging
import sys
from pathlib import Path

from .tools.helper_functions import HelperFunctions as HF
from .output.shared_structure import LBSNRecordDicts
from .output.submit_data import LBSNTransfer
from .input.load_data import LoadData


class LBSNTransform():
    """Import, convert and export RAW Location Based Social Media data,
    such as Twitter and Flickr, based on a common data structure concept
    in Google's ProtoBuf format (see package lbsnstructure).

    Input can be:
        - local CSV or Json (stacked/regular/line separated)
        - Postgres DB connection
    Output can be:
        - local CSV
        - local file with ProtoBuf encoded records
        - local SQL file ready for "Import from" in Postgres LBSN db
        - Postgres DB connection (with existing LBSN DB Structure)

    Parameters
    ----------

    origin_id : int, optional (default=3)
        Type of input source. Each input source has its own import mapper
        defined in a class. Feel free to add or modify classes based
        on your needs. Pre-provided are:
            2    - Flickr
            2.1  - Flickr YFCC100M dataset
            3    - Twitter
    """

    def __init__(
            self, origin_id=3, logging_level=None,
            is_local_input: bool = False, transfer_count: int = 50000,
            csv_output: bool = True, csv_suppress_linebreaks: bool = True,
            dbuser_output=None, dbserveraddress_output=None, dbname_output=None,
            dbpassword_output=None, dbserverport_output=None,
            dbuser_input=None, dbserveraddress_input=None, dbname_input=None,
            dbpassword_input=None, dbserverport_input=None,
            dbformat_output=None, dbuser_hllworker=None,
            dbserveraddress_hllworker=None, dbname_hllworker=None,
            dbpassword_hllworker=None, dbserverport_hllworker=None,
            include_lbsn_bases=None):
        """Init settings for LBSNTransform"""

        # init logger level
        if logging_level is None:
            logging_level = logging.INFO
        # Set Output to Replace in case of encoding issues (console/windows)
        sys.stdout = io.TextIOWrapper(
            sys.stdout.detach(), sys.stdout.encoding, 'replace')
        sys.stdout.flush()
        self.log = HF.set_logger()

        # init global settings

        self.transfer_count = transfer_count
        self.importer = HF.load_importer_mapping_module(
            origin_id)
        # get origin name and id from importer
        # e.g. yfcc100m dataset has origin id 21,
        # but is specified as general Flickr origin (2) in importer
        self.origin_id = self.importer.ORIGIN_ID
        self.origin_name = self.importer.ORIGIN_NAME
        # establish output connection
        self.dbuser_output = dbuser_output
        conn_output, cursor_output = LoadData.initialize_connection(
            dbuser_output, dbserveraddress_output,
            dbname_output, dbpassword_output, dbserverport_output)
        if dbformat_output == "hll":
            __, cursor_hllworker = LoadData.initialize_connection(
                dbuser_hllworker, dbserveraddress_hllworker,
                dbname_hllworker, dbpassword_hllworker, dbserverport_hllworker,
                readonly=True)
        else:
            cursor_hllworker = None

        # store global for closing connection later
        self.cursor_output = cursor_output
        self.output = LBSNTransfer(
            db_cursor=cursor_output,
            db_connection=conn_output,
            store_csv=csv_output,
            SUPPRESS_LINEBREAKS=csv_suppress_linebreaks,
            dbformat_output=dbformat_output,
            hllworker_cursor=cursor_hllworker,
            include_lbsn_bases=include_lbsn_bases)
        # load from local json/csv or from PostgresDB
        self.cursor_input = None
        self.is_local_input = is_local_input
        if not self.is_local_input:
            __, cursor_input = LoadData.initialize_connection(
                dbuser_input, dbserveraddress_input,
                dbname_input, dbpassword_input, dbserverport_input,
                readonly=True, dict_cursor=True)
            self.cursor_input = cursor_input
        #      loc_filelist = LoadData.read_local_files(config)
        # else:
        #      # establish input connection
        #

        # initialize stats
        self.processed_total = 0
        self.initial_loop = True
        self.how_long = None
        # field mapping structure
        # this is where all the converted data will be stored
        # note that one input record may contain many lbsn records
        self.lbsn_records = LBSNRecordDicts()

    def add_processed_records(self, lbsn_record):
        """Adds one or multiple LBSN Records (ProtoBuf)
        to collection (dicts of LBSNRecords)

        Will automatically call self.store_lbsn_records()
        """
        self.lbsn_records.add_records_to_dict(
            lbsn_record)
        self.processed_total += 1
        # On the first loop
        # or after 50.000 (default) processed records,
        # store results
        if self.initial_loop:
            if self.output.dbformat_output == 'lbsn':
                self.output.store_origin(
                    self.origin_id, self.origin_name)
                self.store_lbsn_records()
            self.initial_loop = False
        if self.lbsn_records.count_glob >= self.transfer_count:
            print("\n", end='')
            self.store_lbsn_records()

    def store_lbsn_records(self):
        """Stores processed LBSN Records to chosen outpur format
        """
        self.output.store_lbsn_record_dicts(self.lbsn_records)
        self.output.commit_changes()
        self.lbsn_records.clear()

    def finalize_output(self):
        """finalize all transactions (csv merge etc.)
        """
        self.store_lbsn_records()
        self.output.finalize()
        # Close connections to DBs
        if not self.is_local_input:
            self.cursor_input.close()
        if self.dbuser_output:
            self.cursor_output.close()

    @staticmethod
    def close_log():
        """"Closes log and writes to archive file
        """
        logging.shutdown()
        # rename log file for archive purposes
        today = HF.get_str_formatted_today()
        outfile = Path(f"{today}.log")
        with open(outfile, 'a+') as outfile:
            with open('log.log') as infile:
                outfile.write(f'\n')
                for line in infile:
                    outfile.write(line)
