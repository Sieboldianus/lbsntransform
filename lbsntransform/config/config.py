# -*- coding: utf-8 -*-

"""
Config module for parsing input args for lbsntransform package.
"""

# pylint: disable=no-member

import argparse
import logging
from pathlib import Path

from shapely import geos

from lbsnstructure import lbsnstructure_pb2 as lbsn
from lbsntransform import __version__


class BaseConfig():
    """Base config class for handling typical input params"""

    def __init__(self):
        """Set Default Config options here

        - or define options as input args
        """
        self.origin = 3
        self.is_local_input = False
        self.local_file_type = 'json'
        self.input_path = None
        self.is_stacked_json = False
        self.is_line_separated_json = False
        self.dbuser_input = 'example-user-name'
        self.dbpassword_input = 'example-user-password'
        self.dbserveraddress_input = '222.22.222.22'
        self.dbserverport_input = 5432
        self.dbformat_input = 'json'
        self.dbname_input = 'test_db2'
        self.dbname_hllworker = None
        self.dbuser_hllworker = None
        self.dbpassword_hllworker = None
        self.dbserveraddress_hllworker = None
        self.dbserverport_hllworker = 5432
        self.dbname_hllworker = None
        self.dbuser_output = None
        self.dbformat_output = 'lbsn'
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

    def parse_args(self):
        """Process input *args

        All args are optional, but some groups need to be defined together.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--version',
                            action='version',
                            version=f'lbsntransform {__version__}')
        parser.add_argument('-o', "--origin",
                            default=self.origin,
                            help='Type of input source. '
                            'Defaults to 3: Twitter '
                            '(1 - Instagram, 2 - Flickr, 3 - Twitter)',
                            type=int)
        # Local Input
        local_input_args = parser.add_argument_group('Local Input')
        local_input_args.add_argument('-l', "--file_input",
                                      action='store_true',
                                      default=False,
                                      help='Process data from files, e.g. json '
                                      'or csv (including '
                                      'urls to files or a folder). '
                                      'Otherwise database input will '
                                      'be assumed.')
        local_input_args.add_argument("--file_type",
                                      default=self.local_file_type,
                                      help='If "--file_input" is set, '
                                      'specify filetype (json, csv etc.)',
                                      type=str)
        local_input_args.add_argument("--input_path_url",
                                      default=self.input_path,
                                      help='Optionally provide path to '
                                      'input folder, otherwise subfolder '
                                      './Input/ will be used. You can also '
                                      'provide a web-url starting with http, '
                                      'which will be accessed using '
                                      'requests.get(url, stream=True). '
                                      'To separate multiple urls, use '
                                      'semicolon (;).',
                                      type=str)
        local_input_args.add_argument("--is_stacked_json",
                                      action='store_true',
                                      default=False,
                                      help='Typical form is '
                                      '[{json1},{json2}], '
                                      'if is_stacked_json is set: '
                                      'will process stacked jsons in the form '
                                      'of {json1}{json2} (no comma)')
        local_input_args.add_argument("--is_line_separated_json",
                                      action='store_true',
                                      default=False,
                                      help='Typical form is '
                                      '[{json1},{json2}], '
                                      'if is_line_separated_json is set: '
                                      'will process stacked jsons in the form '
                                      'of {json1}\n{json2} (linebreak)')
        # HLL Worker
        hllworker_args = parser.add_argument_group('HLL Worker')
        hllworker_args.add_argument("--dbpassword_hllworker",
                                    default=self.dbpassword_hllworker,
                                    help='Password for hllworker db',
                                    type=str)
        hllworker_args.add_argument("--dbuser_hllworker",
                                    default=self.dbuser_hllworker,
                                    help='Username for hllworker db. ',
                                    type=str)
        hllworker_args.add_argument("--dbserveraddress_hllworker",
                                    default=self.dbserveraddress_hllworker,
                                    help='IP Address for hllworker db, '
                                    'e.g. 111.11.11.11 . Optionally add '
                                    'port to use, e.g. 111.11.11.11:5432. '
                                    '5432 is the default port',
                                    type=str)
        hllworker_args.add_argument("--dbname_hllworker",
                                    default=self.dbname_hllworker,
                                    help='DB name for hllworker db, ',
                                    type=str)
        # DB Output
        dboutput_args = parser.add_argument_group('DB Output')
        dboutput_args.add_argument('-p', "--dbpassword_output",
                                   default=self.dbpassword_output,
                                   help='Password for output postgres db',
                                   type=str)
        dboutput_args.add_argument('-u', "--dbuser_output",
                                   default=self.dbuser_output,
                                   help='Username for output postgres db. '
                                   'Default: example-user-name2',
                                   type=str)
        dboutput_args.add_argument('-a', "--dbserveraddress_output",
                                   default=self.dbserveraddress_output,
                                   help='IP Address for output db, '
                                   'e.g. 111.11.11.11 . Optionally add '
                                   'port to use, e.g. 111.11.11.11:5432. '
                                   '5432 is the default port',
                                   type=str)
        dboutput_args.add_argument('-n', "--dbname_output",
                                   default=self.dbname_output,
                                   help='DB name for output db, '
                                   'e.g.: "test_db"',
                                   type=str)
        dboutput_args.add_argument("--dbformat_output",
                                   default=self.dbformat_output,
                                   help='The format of the output db, '
                                   'either "hll" or "lbsn". This setting '
                                   'affects how data is stored, either '
                                   'anonymized and aggregated (hll) or in '
                                   'its original structure (lbsn).',
                                   type=str)
        # DB Input
        dbinput_args = parser.add_argument_group('DB Input')
        dbinput_args.add_argument("--dbpassword_input",
                                  default=self.dbpassword_input,
                                  help='Password for input postgres db',
                                  type=str)
        dbinput_args.add_argument("--dbuser_input",
                                  default=self.dbuser_input,
                                  help='Username for input postgres db. '
                                  'Default: example-user-name',
                                  type=str)
        dbinput_args.add_argument("--dbserveraddress_input",
                                  default=self.dbserveraddress_input,
                                  help='IP Address for input db, '
                                  'e.g. 111.11.11.11. Optionally add '
                                  'port to use, e.g. 111.11.11.11:5432. '
                                  '5432 is the default port',
                                  type=str)
        dbinput_args.add_argument("--dbname_input",
                                  default=self.dbname_input,
                                  help='DB name for input db, '
                                  'e.g.: test_db',
                                  type=str)
        dbinput_args.add_argument("--dbformat_input",
                                  default=self.dbformat_input,
                                  help='The format of the input db, '
                                  'either "lbsn" or "json".',
                                  type=str)
        # Additional args
        settings_args = parser.add_argument_group('Additional settings')
        settings_args.add_argument('-t', "--transferlimit",
                                   default=self.transferlimit,
                                   help='Limit the number of records to '
                                   'process. Defaults to None (= process all).',
                                   type=int)
        settings_args.add_argument("--transfer_count",
                                   default=self.transfer_count,
                                   help='Default to 50k: After how many '
                                   'parsed records should the result be '
                                   'transferred to the DB. Larger values '
                                   'improve speed, because duplicate '
                                   'check happens in Python and not in '
                                   'Postgres Coalesce; however, they\'re also '
                                   'heavier on memory.',
                                   type=int)
        settings_args.add_argument("--records_tofetch",
                                   default=self.number_of_records_to_fetch,
                                   help='If retrieving from a db, limit the '
                                   'number of records to fetch at once. '
                                   'Defaults to 10k', type=int)
        settings_args.add_argument(
            "--disable_transfer_reactions",
            action='store_true',
            help='Disable transfer of reactions '
            '(reactions will be skipped, only original posts are transferred)')
        settings_args.add_argument(
            "--disable_reaction_post_referencing",
            action='store_true',
            default=False,
            help='Enable this option in args to prevent empty posts stored '
            'due to Foreign Key Exists Requirement '
            'e.g. 0 = Save Original Tweets of Retweets in "posts"; 1 = do not '
            'store Original Tweets of Retweets; !Not implemented: 2 = Store '
            'Original Tweets of Retweets as "post_reactions"')
        settings_args.add_argument("--ignore_non_geotagged",
                                   action='store_true',
                                   help='Ignore posts that are not geotagged.')
        settings_args.add_argument("--startwith_db_rownumber",
                                   help='Provide a number (row-id) to start '
                                   'processing from live db', type=int)
        settings_args.add_argument("--endwith_db_rownumber",
                                   help='Provide a number (row-id) to end '
                                   'processing from live db', type=int)
        settings_args.add_argument("--debug_mode",
                                   help='Enable debug mode (not implemented).',
                                   type=str)
        settings_args.add_argument("--geocode_locations",
                                   default=self.geocode_locations,
                                   help='Provide path to CSV file with '
                                   'location geocodes (CSV Structure: '
                                   'lat, lng, name. Defaults to None.',
                                   type=str)
        settings_args.add_argument("--ignore_input_source_list",
                                   default=self.ignore_input_source_list,
                                   help='Provide a path to a list of input_source '
                                   'types that will be ignored (e.g. to '
                                   'ignore certain bots etc.)',
                                   type=str)
        settings_args.add_argument("--input_lbsn_type",
                                   default=self.input_lbsn_type,
                                   help='Input type, e.g. "post", "profile", '
                                   '"friendslist", "followerslist" etc. '
                                   'Used to select appropiate mapping '
                                   'procedure.',
                                   type=str)
        settings_args.add_argument("--map_full_relations",
                                   action='store_true',
                                   help='Set to true to map full relations, '
                                   'e.g. many-to-many relationships, '
                                   'such as user_follows, '
                                   'user_friend, user_mentions etc. are '
                                   'mapped in a separate table. '
                                   'Defaults to False.')
        settings_args.add_argument("--csv_output",
                                   action='store_true',
                                   default=self.csv_output,
                                   help='If set will output all '
                                   'submit values to local CSV instead.')
        settings_args.add_argument("--csv_allow_linebreaks",
                                   action='store_true',
                                   help='If set will not '
                                   'remove intext-linebreaks (\r or \n) '
                                   'in output CSVs')
        settings_args.add_argument("--csv_delimiter",
                                   default=None,
                                   help=repr(
                                       'Provide CSV delimiter to use. '
                                       'Default is comma(,). Note: to pass tab, '
                                       'use variable substitution ($"\t")'),
                                   type=str)
        settings_args.add_argument("--recursive_load",
                                   action='store_true', default=False,
                                   help='If set, process input directories '
                                   'recursively (default depth: 2)')
        settings_args.add_argument("--skip_until_file",
                                   default=self.skip_until_file,
                                   help='If local input, skip all files '
                                   'until file with name x appears '
                                   '(default: start immediately)',
                                   type=str)
        settings_args.add_argument("--min_geoaccuracy",
                                   default=self.min_geoaccuracy,
                                   help='Set to "latlng", "place", '
                                   'or "city" to limit output based '
                                   'on min geoaccuracy',
                                   type=str)

        args = parser.parse_args()
        if args.file_input:
            self.is_local_input = True
            self.local_file_type = args.file_type
            if args.is_stacked_json:
                self.is_stacked_json = True
            if args.is_line_separated_json:
                self.is_line_separated_json = True
            if not args.input_path_url:
                self.input_path = Path.cwd() / "01_Input"
                print(f'Using Path: {self.input_path_url}')
            else:
                if str(args.input_path_url).startswith('http'):
                    self.input_path = args.input_path_url.split(";")
                    self.source_web = True
                else:
                    input_path = Path(args.input_path_url)
                    self.input_path = input_path
        else:
            self.dbuser_input = args.dbuser_input
            self.dbpassword_input = args.dbpassword_input
            input_ip, input_port = BaseConfig.get_ip_port(
                args.dbserveraddress_input)
            self.dbserveraddress_input = input_ip
            if input_port:
                self.dbserverport_input = input_port
            self.dbname_input = args.dbname_input
        if args.dbformat_input:
            self.dbformat_input = args.dbformat_input
        if args.origin:
            self.origin = args.origin
        if args.geocode_locations:
            self.geocode_locations = Path(
                args.geocode_locations)
        if args.ignore_input_source_list:
            self.ignore_input_source_list = Path(
                args.ignore_input_source_list)
        if args.dbuser_output:
            self.dbuser_output = args.dbuser_output
            self.dbpassword_output = args.dbpassword_output
            output_ip, output_port = BaseConfig.get_ip_port(
                args.dbserveraddress_output)
            self.dbserveraddress_output = output_ip
            if output_port:
                self.dbserverport_output = output_port
            self.dbname_output = args.dbname_output
        if args.dbformat_output:
            self.dbformat_output = args.dbformat_output
            if self.dbformat_output == "hll":
                try:
                    self.dbname_hllworker = args.dbname_hllworker
                    self.dbuser_hllworker = args.dbuser_hllworker
                    self.dbpassword_hllworker = args.dbpassword_hllworker
                    hllworker_ip, hllworker_port = BaseConfig.get_ip_port(
                        args.dbserveraddress_hllworker)
                    self.dbserveraddress_hllworker = hllworker_ip
                    if hllworker_port:
                        self.dbserverport_hllworker = hllworker_port
                except ValueError:
                    raise ValueError(
                        "If '--dbformat_output hll' is used, also provide "
                        "a HLL Worker Connection (--dbname_hllworker, "
                        "--dbuser_hllworker, --dbpassword_hllworker, "
                        "--dbserveraddress_hllworker)")
        if args.transferlimit:
            self.transferlimit = args.transferlimit
            if self.transferlimit == 0:
                self.transferlimit = None
        if args.transfer_count:
            self.transfer_count = args.transfer_count
        if args.records_tofetch:
            self.number_of_records_to_fetch = args.records_tofetch
        if args.disable_transfer_reactions:
            self.transfer_reactions = False
        if args.disable_reaction_post_referencing:
            self.disable_reactionpost_ref = True
        if args.ignore_non_geotagged:
            self.ignore_non_geotagged = True
        if args.startwith_db_rownumber:
            self.startwith_db_rownumber = args.startwith_db_rownumber
        if args.endwith_db_rownumber:
            self.endwith_db_rownumber = args.endwith_db_rownumber
        if args.debug_mode:
            self.debug_mode = args.debug_mode
        if args.input_lbsn_type:
            self.input_lbsn_type = args.input_lbsn_type
        if args.map_full_relations:
            self.map_relations = True
        if args.csv_output:
            self.csv_output = True
        if args.csv_allow_linebreaks:
            self.csv_suppress_linebreaks = False
        if args.csv_delimiter:
            self.csv_delim = args.csv_delimiter
        if args.recursive_load:
            self.recursive_load = True
        if args.skip_until_file:
            self.skip_until_file = args.skip_until_file
        if args.min_geoaccuracy:
            self.min_geoaccuracy = self.check_geoaccuracy_input(
                args.min_geoaccuracy)

    @staticmethod
    def check_geoaccuracy_input(geoaccuracy_string):
        """Checks geoaccuracy input string and matches
        against proto buf spec
        """
        if geoaccuracy_string == 'latlng':
            return lbsn.Post.LATLNG
        if geoaccuracy_string == 'place':
            return lbsn.Post.PLACE
        if geoaccuracy_string == 'city':
            return lbsn.Post.CITY
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
        ip_addr = None
        ip_string_spl = ip_string.split(":")
        if len(ip_string_spl) == 2:
            ip_addr = ip_string_spl[0]
            port = ip_string_spl[1]
        else:
            ip_addr = ip_string
        return ip_addr, port

    @staticmethod
    def set_options():
        """Includes global options in other packages to be set
        prior execution"""
        # tell shapely to include the srid when generating WKBs
        geos.WKBWriter.defaults['include_srid'] = True
