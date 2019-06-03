# -*- coding: utf-8 -*-

"""
Config module for parsing input args for lbsntransform package.
"""

# pylint: disable=no-member

from pathlib import Path
import argparse
import os
import sys
from shapely import geos
import logging
from lbsnstructure.lbsnstructure_pb2 import lbsnPost


class BaseConfig():
    def __init__(self):
        """Set Default Config options here

        - or define options as input args
        """
        self.origin = 3
        self.is_local_input = False
        self.local_file_type = 'json'
        self.input_path = None
        self.is_stacked_json = False
        self.dbuser_input = 'example-user-name'
        self.dbpassword_input = 'example-user-password'
        self.dbserveraddress_input = '222.22.222.22'
        self.dbserverport_input = 5432
        self.dbname_input = 'test_db2'
        self.dbuser_output = None
        self.dbpassword_output = None
        self.dbserveraddress_output = None
        self.dbserverport_output = 5432
        self.dbname_output = None
        self.transferlimit = None
        self.transfer_count = 50000
        self.number_of_records_to_fetch = 10000
        self.transfer_reactions = True
        self.disable_reactionpost_ref = False
        self.ignore_non_geotagged = False
        self.startwith_db_rownumber = 0
        self.endwith_db_rownumber = None
        self.debug_mode = 'INFO'
        self.geocode_locations = False
        self.ignore_input_source_list = False
        self.input_lbsn_type = None
        self.map_relations = False
        self.csv_output = False
        self.csv_suppress_linebreaks = True
        self.csv_delim = None
        self.recursive_load = False
        self.skip_until_file = None
        self.min_geoaccuracy = None
        self.logging_level = logging.INFO
        self.source_web = False

        BaseConfig.set_options()

    def parseArgs(self):
        """Process input *args

        All args are optional, but some groups need to be defined together.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-sO', "--Origin",
                            default=self.origin,
                            help='Type of input source. '
                            'Defaults to 3: Twitter '
                            '(1 - Instagram, 2 - Flickr, 3 - Twitter)')
        # Local Input
        local_input_args = parser.add_argument_group('Local Input')
        local_input_args.add_argument('-lI', "--LocalInput",
                                      action='store_true',
                                      default=False,
                                      help='Process local json or csv')
        local_input_args.add_argument('-lT', "--LocalFileType",
                                      default=self.local_file_type,
                                      help='If localread, '
                                      'specify filetype (json, csv etc.)')
        local_input_args.add_argument('-iP', "--InputPath",
                                      default=self.input_path,
                                      help='Optionally provide path to '
                                      'input folder, otherwise '
                                      './Input/ will be used. You can also '
                                      'provide a web-url starting with http')
        local_input_args.add_argument('-iS', "--isStackedJson",
                                      action='store_true',
                                      default=False,
                                      help='Typical form is '
                                      '[{json1},{json2}], '
                                      'if is_stacked_json is True: '
                                      'will process stacked jsons in the form '
                                      'of {json1}{json2} (no comma)')
        # DB Output
        dboutput_args = parser.add_argument_group('DB Output')
        dboutput_args.add_argument('-pO', "--dbPassword_Output",
                                   default=self.dbpassword_output,
                                   help='')
        dboutput_args.add_argument('-uO', "--dbUser_Output",
                                   default=self.dbuser_output,
                                   help='Default: example-user-name2')
        dboutput_args.add_argument('-aO', "--dbServeraddressOutput",
                                   default=self.dbserveraddress_output,
                                   help='e.g. 111.11.11.11 . Optionally add '
                                   'port to use, e.g. 111.11.11.11:5432. '
                                   '5432 is the default port')
        dboutput_args.add_argument('-nO', "--dbNameOutput",
                                   default=self.dbname_output,
                                   help='e.g.: test_db')
        # DB Input
        dbinput_args = parser.add_argument_group('DB Input')
        dbinput_args.add_argument('-pI', "--dbPassword_Input",
                                  default=self.dbpassword_input,
                                  help='')
        dbinput_args.add_argument('-uI', "--dbUser_Input",
                                  default=self.dbuser_input,
                                  help='Default: example-user-name')
        dbinput_args.add_argument('-aI', "--dbServeraddressInput",
                                  default=self.dbserveraddress_input,
                                  help='e.g. 111.11.11.11. Optionally add '
                                  'port to use, e.g. 111.11.11.11:5432. '
                                  '5432 is the default port')
        dbinput_args.add_argument('-nI', "--dbNameInput",
                                  default=self.dbname_input,
                                  help='e.g.: test_db')
        # Additional args
        settings_args = parser.add_argument_group('Additional settings')
        settings_args.add_argument('-t', "--transferlimit",
                                   default=self.transferlimit,
                                   help='')
        settings_args.add_argument('-tC', "--transferCount",
                                   default=self.transfer_count,
                                   help='Default to 50k: After how many '
                                   'parsed records should the result be '
                                   'transferred to the DB. Larger values '
                                   'improve speed, because duplicate '
                                   'check happens in Python and not in '
                                   'Postgres Coalesce; larger values are '
                                   'heavier on memory.')
        settings_args.add_argument('-nR', "--numberOfRecordsToFetch",
                                   default=self.number_of_records_to_fetch,
                                   help='')
        settings_args.add_argument(
            '-tR', "--disableTransferReactions",
            action='store_true',
            help='')
        settings_args.add_argument(
            '-rR', "--disableReactionPostReferencing",
            action='store_true',
            default=False,
            help='Enable this option in args to prevent empty posts stored '
            'due to Foreign Key Exists Requirement '
            '0 = Save Original Tweets of Retweets in "posts"; 1 = do not '
            'store Original Tweets of Retweets; !Not implemented: 2 = Store '
            'Original Tweets of Retweets as "post_reactions"')
        settings_args.add_argument('-iG', "--ignoreNonGeotagged",
                                   action='store_true',
                                   default=self.ignore_non_geotagged,
                                   help='')
        settings_args.add_argument('-rS', "--startWithDBRowNumber",
                                   default=self.startwith_db_rownumber,
                                   help='')
        settings_args.add_argument('-rE', "--endWithDBRowNumber",
                                   default=self.endwith_db_rownumber,
                                   help='')
        settings_args.add_argument('-d', "--debugMode",
                                   default=self.debug_mode,
                                   help='Needs to be implemented.')
        settings_args.add_argument('-gL', "--geocodeLocations",
                                   default=self.geocode_locations,
                                   help='Defaults to None. '
                                   'Provide path to CSV file with '
                                   'location geocodes (CSV Structure: '
                                   'lat, lng, name)')
        settings_args.add_argument('-igS', "--ignoreInputSourceList",
                                   default=self.ignore_input_source_list,
                                   help='Provide a list of input_source '
                                   'types that will be ignored (e.g. to '
                                   'ignore certain bots etc.)')
        settings_args.add_argument('-iT', "--inputType",
                                   default=self.input_lbsn_type,
                                   help='Input type, e.g. "post", "profile", '
                                   '"friendslist", "followerslist" etc.')
        settings_args.add_argument('-mR', "--mapFullRelations",
                                   action='store_true',
                                   help='Defaults to False. Set to true '
                                   'to map full relations, e.g. many-to-many '
                                   'relationships such as user_follows, '
                                   'user_friend, user_mentions etc. are '
                                   'mapped in a separate table')
        settings_args.add_argument('-CSV', "--CSVOutput",
                                   action='store_true',
                                   default=self.csv_output,
                                   help='Set to True to Output all '
                                   'Submit values to CSV')
        settings_args.add_argument('-CSVal', "--CSVallowLinebreaks",
                                   action='store_true', default=False,
                                   help='If set to False will not '
                                   'remove intext-linebreaks (\r or \n) '
                                   'in output CSVs')
        settings_args.add_argument('-CSVdelim', "--CSVdelimitor",
                                   default=None,
                                   help=repr(
                                       'Provide CSV delimitor to use. '
                                       'Default is comma(,). Note: to pass tab, '
                                       'use variable substitution ($"\t")'))
        settings_args.add_argument('-rL', "--recursiveLoad",
                                   action='store_true', default=False,
                                   help='Process Input Directories '
                                   'recursively (depth: 2)')
        settings_args.add_argument('-sF', "--skipUntilFile",
                                   default=self.skip_until_file,
                                   help='If local input, skip all files '
                                   'until file with name x appears '
                                   '(default: start immediately)')
        settings_args.add_argument('-mGA', "--minGeoAccuracy",
                                   default=self.min_geoaccuracy,
                                   help='Set to "latlng", "place", '
                                   'or "city" to limit output based '
                                   'on min geoaccuracy')

        args = parser.parse_args()
        if args.LocalInput:
            self.is_local_input = True
            self.local_file_type = args.LocalFileType
            if args.isStackedJson:
                self.is_stacked_json = True
            if not args.InputPath:
                self.input_path = Path.cwd() / "01_Input"
                print(f'Using Path: {self.input_path}')
            else:
                if str(args.InputPath).startswith('http'):
                    self.input_path = str(args.InputPath)
                    self.source_web = True
                else:
                    input_path = Path(args.InputPath)
                    self.input_path = input_path
        else:
            self.dbuser_input = args.dbUser_Input
            self.dbpassword_input = args.dbPassword_Input
            input_ip, input_port = BaseConfig.get_ip_port(
                args.dbServeraddressInput)
            self.dbserveraddress_input = input_ip
            if input_port:
                self.dbserverport_input = input_port
            self.dbname_input = args.dbNameInput
        if args.Origin:
            self.origin = int(args.Origin)
        if args.geocodeLocations:
            self.geocode_locations = f'{os.getcwd()}\\'
            f'{args.geocodeLocations}'
        if args.ignoreInputSourceList:
            self.ignore_input_source_list = f'{os.getcwd()}\\'
            f'{args.ignoreInputSourceList}'
        if args.dbUser_Output:
            self.dbuser_output = args.dbUser_Output
            self.dbpassword_output = args.dbPassword_Output
            output_ip, output_port = BaseConfig.get_ip_port(
                args.dbServeraddressOutput)
            self.dbserveraddress_output = output_ip
            if output_port:
                self.dbserverport_output = output_port
            self.dbname_output = args.dbNameOutput
        if args.transferlimit:
            self.transferlimit = int(args.transferlimit)
            if self.transferlimit == 0:
                self.transferlimit = None
        if args.transferCount:
            self.transfer_count = int(args.transferCount)
        if args.numberOfRecordsToFetch:
            self.number_of_records_to_fetch = int(args.numberOfRecordsToFetch)
        if args.disableTransferReactions is True:
            self.transfer_reactions = False
        if args.disableReactionPostReferencing:
            self.disable_reactionpost_ref = True
        self.ignore_non_geotagged = args.ignoreNonGeotagged
        if args.startWithDBRowNumber:
            self.startwith_db_rownumber = int(args.startWithDBRowNumber)
        if args.endWithDBRowNumber:
            self.endwith_db_rownumber = int(args.endWithDBRowNumber)
        self.debug_mode = args.debugMode
        if args.inputType:
            self.input_lbsn_type = args.inputType
        if args.mapFullRelations:
            self.map_relations = True
        if args.CSVOutput:
            self.csv_output = True
        if args.CSVallowLinebreaks:
            self.csv_suppress_linebreaks = False
        if args.CSVdelimitor:
            self.csv_delim = args.CSVdelimitor
        if args.recursiveLoad:
            self.recursive_load = True
        if args.skipUntilFile:
            self.skip_until_file = args.skipUntilFile
        if args.minGeoAccuracy:
            self.min_geoaccuracy = self.check_geoaccuracy_input(
                args.minGeoAccuracy)

    @staticmethod
    def check_geoaccuracy_input(geoaccuracy_string):
        """Checks geoaccuracy input string and matches
        against proto buf spec
        """
        if geoaccuracy_string == 'latlng':
            return lbsnPost.LATLNG
        elif geoaccuracy_string == 'place':
            return lbsnPost.PLACE
        elif geoaccuracy_string == 'city':
            return lbsnPost.CITY
        else:
            print("Unknown geoaccuracy.")
            return None

    @staticmethod
    def get_ip_port(ip_string: str):
        """Gets IP and port, if available

        Arguments:
            ip_string {str} -- String containing IPV4 and
            possibly port attached with : character
        """
        port = None
        ip = None
        ip_string_spl = ip_string.split(":")
        if len(ip_string_spl) == 2:
            ip = ip_string_spl[0]
            port = ip_string_spl[1]
        else:
            ip = ip_string
        return ip, port

    @staticmethod
    def set_options():
        """Includes global options in other packages to be set
        prior execution"""
        # tell shapely to include the srid when generating WKBs
        geos.WKBWriter.defaults['include_srid'] = True
