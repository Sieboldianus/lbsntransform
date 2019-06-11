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

from .classes.helper_functions import HelperFunctions as HF
from .classes.helper_functions import LBSNRecordDicts
from .classes.load_data import LoadData
from .classes.submit_data import LBSNTransfer
from .config.config import BaseConfig


class LBSNTransform():
    """Import, convert and export RAW Location Based Social Media data,
    such as Twitter and Flickr, based on a common data structure concept
    in Google's ProtoBuf format (see package lbsnstructure).

    Input can be:
        - local CSV or Json (stacked/regular)
        - Postgres DB connection
    Output can be:
        - local CSV
        - local file with ProtoBuf encoded records
        - local SQL file ready for "Impoort from" in Postgres LBSN db
        - Postgres DB connection

    Parameters
    ----------

    origin : str, optional (default=3)
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
            transferlimit: int = None,
            csv_output: bool = True, csv_suppress_linebreaks: bool = True,
            dbuser_output=None, dbserveraddress_output=None, dbname_output=None,
            dbpassword_output=None, dbserverport_output=None,
            dbuser_input=None, dbserveraddress_input=None, dbname_input=None,
            dbpassword_input=None, dbserverport_input=None):
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
        self.transferlimit = None
        if transferlimit:
            self.transferlimit = transferlimit
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
        # store global for closing connection later
        self.cursor_output = cursor_output
        self.output = LBSNTransfer(
            db_cursor=cursor_output,
            db_connection=conn_output,
            store_csv=csv_output,
            SUPPRESS_LINEBREAKS=csv_suppress_linebreaks)
        # load from local json/csv or from PostgresDB
        self.cursor_input = None
        self.is_local_input = is_local_input
        if not self.is_local_input:
            __, cursor_input = LoadData.initialize_connection(
                dbuser_input, dbserveraddress_input,
                dbname_input, dbpassword_input, dbserverport_input,
                readonly=True)
            self.cursor_input = cursor_input
        #      loc_filelist = LoadData.read_local_files(config)
        # else:
        #      # establish input connection
        #

        # initialize stats
        self.processed_records = 0
        self.processed_total = 0
        self.skipped_low_geoaccuracy = 0
        self.initial_loop = True
        self.max_records = None
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
        self.processed_records += 1
        # On the first loop
        # or after 50.000 (default) processed records,
        # store results
        if (self.initial_loop or
                self.processed_records >= self.transfer_count):
            self.output.store_origin(self.origin_id, self.origin_name)
            self.store_lbsn_records()
        if self.initial_loop:
            self.initial_loop = False

    def store_lbsn_records(self):
        """Stores processed LBSN Records to chosen outpur format
        """
        self.output.store_lbsn_record_dicts(self.lbsn_records)
        self.output.commit_changes()
        self.lbsn_records.clear()
        # update statistics
        self.processed_total += self.processed_records
        self.processed_records = 0
        self.continue_number = 0
        self.start_number = 0

        if self.transferlimit:
            self.max_records = self.transferlimit - self.processed_total

    def finalize_output(self):
        """finalize all transactions (csv merge etc.)
        """
        self.output.finalize()
        # Close connections to DBs
        if not self.is_local_input:
            self.cursor_input.close()
        if self.dbuser_output:
            self.cursor_output.close()
