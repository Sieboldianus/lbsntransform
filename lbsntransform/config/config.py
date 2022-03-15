# -*- coding: utf-8 -*-

"""
Config module for parsing input args for lbsntransform package.
"""

# pylint: disable=no-member

import argparse
import logging
from pathlib import Path
from typing import List, Tuple

from shapely import geos

from lbsnstructure import lbsnstructure_pb2 as lbsn
from lbsntransform import __version__


class BaseConfig():
    """Base config class for handling typical input params"""

    def __init__(self):
        """Set Default Config options here

        - or define options as input args
        """
        self.origin = 0
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
        self.startwith_db_rownumber = None
        self.endwith_db_rownumber = None
        self.debug_mode = 'INFO'
        self.geocode_locations = False
        self.ignore_input_source_list = False
        self.input_lbsn_type = None
        self.map_relations = False
        self.csv_output = False
        self.csv_suppress_linebreaks = True
        self.csv_delim = None
        self.use_csv_dictreader = None
        self.recursive_load = False
        self.skip_until_file = None
        self.min_geoaccuracy = None
        self.logging_level = logging.INFO
        self.source_web = False
        self.skip_until_record = None
        self.zip_records = None
        self.include_lbsn_objects = []
        self.include_lbsn_bases = None
        self.override_lbsn_query_schema = None
        self.mappings_path = None
        self.dry_run = None
        self.hmac_key = None

        BaseConfig.set_options()

    @staticmethod
    def get_arg_parser(
            parser: argparse.ArgumentParser = None) -> argparse.ArgumentParser:
        """Define lbsntransform cli arguments

        Arguments:
            parser: Optional parser with extended arguments. This
            can be used to include lbsntransofmr in another package.

        Note: All args are optional, but some groups need to be defined
            together.
        """
        if parser is None:
            parser = argparse.ArgumentParser()
        parser.add_argument('--version',
                            action='version',
                            version=f'lbsntransform {__version__}')
        parser.add_argument('-o', "--origin",
                            default=0,
                            help='Input source type (id). '
                            '  '
                            '  '
                            '* Defaults to `0`: LBSN  '
                            '  '
                            'Other possible values:  '
                            '* `1` - Instagram  '
                            '* `2` - Flickr  '
                            '* `21` - Flickr YFCC100M  '
                            '* `3` - Twitter  ',
                            type=int)
        parser.add_argument("--dry-run",
                            action='store_true',
                            help='Perform a trial run '
                            '  '
                            'with no changes made '
                            'to database/output')
        # Local Input
        local_input_args = parser.add_argument_group('Local Input')
        local_input_args.add_argument('-l', "--file_input",
                                      action='store_true',
                                      help='This flag enables file input  '
                                      '  '
                                      '(instead of reading data from a database). '
                                      '  '
                                      '  '
                                      '* To specify which files to process, see '
                                      'parameter `--input_path_url`.  '
                                      '* To specify file types, e.g. whether to '
                                      'process data from `json` '
                                      'or `csv`, or from URLs,  '
                                      '  see `--file_type`  ')
        local_input_args.add_argument("--file_type",
                                      default='json',
                                      help='Specify filetype  '
                                      '  '
                                      ' (`json`, `csv` etc.) '
                                      '  '
                                      '  '
                                      '* only applies if `--file_input` is used.  ',
                                      type=str)
        local_input_args.add_argument("--input_path_url",
                                      default="01_Input",
                                      help='Path to input folder.  '
                                      '  '
                                      '* If not provided, subfolder `./01_Input/` '
                                      ' will be used.  '
                                      '* You can also provide a web-url, '
                                      'starting with `http(s)`  '
                                      '* URLs will be accessed using '
                                      '`requests.get(url, stream=True)`.  '
                                      '* To separate multiple urls, use '
                                      'semicolon (`;`). In this case, see also '
                                      '`--zip_records`.  ',
                                      type=str)
        local_input_args.add_argument("--is_stacked_json",
                                      action='store_true',
                                      default=False,
                                      help='Input is stacked json. '
                                      '  '
                                      '  '
                                      '* The typical form of json is '
                                      '`[{json1},{json2}]`  '
                                      '* If `--is_stacked_json` is set, '
                                      'it will process stacked jsons in the form '
                                      'of `{json1}{json2}` (no comma)  ')
        local_input_args.add_argument("--is_line_separated_json",
                                      action='store_true',
                                      default=False,
                                      help='Json is line separated '
                                      '  '
                                      '  '
                                      '* The typical form is '
                                      '`[{json1},{json2}]`  '
                                      '* If `--is_line_separated_json` is set, '
                                      'it will process stacked jsons in the form '
                                      'of `{json1}\n{json2}` (with linebreak)  '
                                      '* Unix style linebreaks (CR) will be used '
                                      'across platforms  '
                                      '* Windows users, use (e.g.) notepad++ to '
                                      'convert from Windows style linebreaks (CRLF)  ')
        # HLL Worker
        hllworker_args = parser.add_argument_group('HLL Worker')
        hllworker_args.add_argument("--dbpassword_hllworker",
                                    help='Password for hllworker db  '
                                    '  '
                                    '  '
                                    '* If reading data into `hlldb`, all '
                                    'HLL Worker parameters must be supplied by'
                                    'default.  '
                                    '* You can substitute hlldb parameters here  '
                                    '* In this case, lbsntransform will use '
                                    'hlldb to convert and union hll sets '
                                    '_and_ to store output results  '
                                    '* Currently, this re-use of hlldb requires '
                                    'to supply the same set of parameters twice  '
                                    '* For separation of concerns, it is recommended '
                                    'to use a separate HLL Worker database  ',
                                    type=str)
        hllworker_args.add_argument("--dbuser_hllworker",
                                    default="postgres",
                                    help='Username for hllworker db.',
                                    type=str)
        hllworker_args.add_argument("--dbserveraddress_hllworker",
                                    help='IP for hllworker db  '
                                    '  '
                                    '  '
                                    '* e.g. `111.11.11.11`  '
                                    '* Optionally add '
                                    'port the to use, e.g. `111.11.11.11:5432`.  '
                                    '* `5432` is the default port  ',
                                    type=str)
        hllworker_args.add_argument("--dbname_hllworker",
                                    help='DB name for hllworker db '
                                    '  '
                                    '  '
                                    '* e.g. `hllworkerdb`  ',
                                    type=str)
        # DB Output
        dboutput_args = parser.add_argument_group('DB Output')
        dboutput_args.add_argument('-p', "--dbpassword_output",
                                   help='Password for out-db  '
                                   '  '
                                   '(postgres raw/hll db)',
                                   type=str)
        dboutput_args.add_argument('-u', "--dbuser_output",
                                   default="postgres",
                                   help='Username for out-db.  '
                                   '  '
                                   'Default: `example-user-name2`',
                                   type=str)
        dboutput_args.add_argument('-a', "--dbserveraddress_output",
                                   help='IP for output db, '
                                   '  '
                                   '  '
                                   '* e.g. `111.11.11.11`  '
                                   '* Optionally add '
                                   'port to use, e.g. `111.11.11.11:5432`.  '
                                   '* `5432` is the default port  ',
                                   type=str)
        dboutput_args.add_argument('-n', "--dbname_output",
                                   help='DB name for output db '
                                   '  '
                                   '  '
                                   '* e.g. `rawdb` or `hlldb`  ',
                                   type=str)
        dboutput_args.add_argument("--dbformat_output",
                                   default="lbsn",
                                   help='Format of the out-db. '
                                   '  '
                                   '  '
                                   '* Either `hll` or `lbsn`.  '
                                   '* This setting '
                                   'affects how data is stored, either '
                                   'in anonymized and aggregate form (`hll`), or in '
                                   'the [lbsn raw structure](https://lbsn.vgiscience.org/structure/) '
                                   '(`lbsn`).  ',
                                   type=str)
        # DB Input
        dbinput_args = parser.add_argument_group('DB Input')
        dbinput_args.add_argument("--dbpassword_input",
                                  help='Password for input-db',
                                  type=str)
        dbinput_args.add_argument("--dbuser_input",
                                  default="postgres",
                                  help='Username for input-db.',
                                  type=str)
        dbinput_args.add_argument("--dbserveraddress_input",
                                  help='IP for input-db, '
                                  '  '
                                  '  '
                                  '* e.g. `111.11.11.11`  '
                                  '* Optionally add port to use, e.g. '
                                  '`111.11.11.11:5432`.  '
                                  '* `5432` is the default port  ',
                                  type=str)
        dbinput_args.add_argument("--dbname_input",
                                  help='DB name for input-db, '
                                  '  '
                                  '  '
                                  '* e.g.: `rawdb`  ',
                                  type=str)
        dbinput_args.add_argument("--dbformat_input",
                                  default="json",
                                  help='Format of the input-db. '
                                  '  '
                                  '  '
                                  '* Either `lbsn` or `json`  '
                                  '* If lbsn is used, the native lbsn raw '
                                  'input mapping (`0`) will be used  '
                                  '* If `json` is used, a custom mapping for '
                                  'json must be provided, for mapping database '
                                  'json\'s to the lbsn structure. See '
                                  '[input mappings](https://lbsn.vgiscience.org/lbsntransform/docs/mappings/#input-mappings)  ',
                                  type=str)
        # Additional args
        settings_args = parser.add_argument_group('Additional settings')
        settings_args.add_argument('-t', "--transferlimit",
                                   help='Abort after x records. '
                                   '  '
                                   '  '
                                   '* This can be used to limit the number of '
                                   'records that will be processed.  '
                                   '* e.g. `--transferlimit 10000` will process '
                                   'the first 10000 input records  '
                                   '* Defaults to None (= process all)  '
                                   '* Note that one input record can map to '
                                   'many output records. This number applies to '
                                   'the number of input records, not the output count.  ',
                                   type=int)
        settings_args.add_argument("--transfer_count",
                                   default=50000,
                                   help='Transfer batch limit x. '
                                   '  '
                                   '  '
                                   '* Defines after how many '
                                   'parsed records the results will be '
                                   'transferred to the DB.  '
                                   '* Defaults to 50000  '
                                   '* If you have a slow server, but a fast machine, larger values '
                                   'improve speed because duplicate '
                                   'check happens in Python, and not in '
                                   'Postgres coalesce;  '
                                   '* However, larger values require '
                                   'more local memory. If you have a fast server, but a slow machine,  '
                                   'Try if smaller batch `--transfer_count` (e.g. 5000) improve spead.  '
                                   '  '
                                   '  '
                                   '!!! note  '
                                   '    Use `--transferlimit` to limit the '
                                   '    total number of records transferred. `--transfer_count` '
                                   '    instead defines the _batch_ count that is used to transfer '
                                   '    data incrementally.  ',
                                   type=int)
        settings_args.add_argument("--records_tofetch",
                                   default=10000,
                                   help='Fetch x records /batch. '
                                   '  '
                                   '  '
                                   '* If retrieving data from a db (`lbsn`), '
                                   'limit the number of records to fetch at once.  '
                                   '* Defaults to 10000  ',
                                   type=int)
        settings_args.add_argument(
            "--disable_transfer_reactions",
            action='store_true',
            help='Disable reactions. '
            '  '
            '  '
            '* If set, processing of lbsn reactions will be skipped,  '
            '* only original posts are transferred.  '
            '* This is usefull to reduce '
            'processing and data footprint for some service data, '
            'e.g. for Twitter, with a large '
            'number of reactions containing little original content.  ')
        settings_args.add_argument(
            "--disable_reaction_post_referencing",
            action='store_true',
            default=False,
            help='Disable reactions-refs. '
            '  '
            '  '
            'Enable this option in args '
            'to prevent empty posts being stored '
            'due to Foreign-Key-Exists Requirement. '
            '  '
            'Possible parameters:  '
            '* `0` = Save Original Tweets of Retweets as `posts`;  '
            '* `1` = do not store Original Tweets of Retweets;  '
            '* `2` = !Not implemented: Store Original Tweets of Retweets as '
            '`post_reactions`  ')
        settings_args.add_argument("--ignore_non_geotagged",
                                   action='store_true',
                                   help='Ignore none-geotagged. '
                                   '  '
                                   '  '
                                   'If set, posts that are not geotagged '
                                   'are ignored during processing.')
        settings_args.add_argument("--startwith_db_rownumber",
                                   help='Start with db row x. '
                                   '  '
                                   '  '
                                   '* Provide a number (row-id) to start '
                                   'processing from live db.  '
                                   '* If input db type '
                                   'is `lbsn`, provide the primary key '
                                   'to start from '
                                   '(e.g. post_guid, place_guid etc.).  '
                                   '* This flag will only work if processing a '
                                   'single lbsn object (e.g. lbsnPost).  ',
                                   type=str)
        settings_args.add_argument("--endwith_db_rownumber",
                                   help='End with db row x. '
                                   '  '
                                   '  '
                                   'Provide a number (row-id) to end '
                                   'processing from live db', type=int)
        settings_args.add_argument("--debug_mode",
                                   help='Enable debug mode.',
                                   type=str)
        settings_args.add_argument("--geocode_locations",
                                   help='Path to loc-geocodes. '
                                   '  '
                                   '  '
                                   '* Provide path to a CSV file with '
                                   'location geocodes  '
                                   '* CSV Header must be: '
                                   '`lat, lng, name`).  '
                                   '* This can be used in mappings to assign '
                                   'coordinates (lat, lng) '
                                   'to use provided locations as text  ',
                                   type=str)
        settings_args.add_argument("--ignore_input_source_list",
                                   help='Path to input ignore. '
                                   '  '
                                   '  '
                                   'Provide a path to a list of input_source '
                                   'types that will be ignored (e.g. to '
                                   'ignore certain bots etc.)',
                                   type=str)
        settings_args.add_argument("--mappings_path",
                                   help='Path mappings folder. '
                                   '  '
                                   '  '
                                   'Provide a path to a custom folder '
                                   'that contains '
                                   'one or more input mapping modules (`*.py`). '
                                   '  '
                                   '  '
                                   '* Have a look at the two sample mappings '
                                   'in [the resources folder](https://gitlab.vgiscience.de/lbsn/lbsntransform/-/tree/master/resources/mappings).  '
                                   '* See how to define custom input mappings '
                                   'in the [docs](https://lbsn.vgiscience.org/lbsntransform/docs/mappings/#input-mappings)  ',
                                   type=str)
        settings_args.add_argument("--input_lbsn_type",
                                   help='Input sub-type '
                                   '  '
                                   '  '
                                   '* e.g. `post`, `profile`, '
                                   '`friendslist`, `followerslist` etc.  '
                                   '* This can be used to select an appropiate '
                                   'mapping procedure in a single mapping module.  ',
                                   type=str)
        settings_args.add_argument("--map_full_relations",
                                   action='store_true',
                                   help='Map full relations. '
                                   '  '
                                   '  '
                                   'Set to true to map full relations, '
                                   'e.g. many-to-many relationships, '
                                   'such as `user_follows`, '
                                   '`user_friend`, or `user_mentions` etc. are '
                                   'mapped in a separate table. '
                                   'Defaults to False.')
        settings_args.add_argument("--csv_output",
                                   action='store_true',
                                   help='Store to local CSV. '
                                   '  '
                                   '  '
                                   'If set, will store all '
                                   'submit values to local CSV instead. '
                                   'Currently, this type of output is not available.')
        settings_args.add_argument("--csv_allow_linebreaks",
                                   action='store_true',
                                   help=repr('Disable linebreak-rem. '
                                   '  '
                                   '  '
                                   'If set, will not '
                                   'remove intext-linebreaks (`\r` or `\n`) '
                                   'in output CSVs')[1:-1])
        settings_args.add_argument("--csv_delimiter",
                                   default=",",
                                   help=repr('CSV delimiter. '
                                             '  '
                                             '  '
                                             '* Provide the CSV delimiter to be used.  '
                                             '* Default is comma (`,`).  '
                                             '* Note: to pass tab, '
                                             'use variable substitution (`$"\t"`)  ')[1:-1],
                                   type=str)
        settings_args.add_argument("--use_csv_dictreader",
                                   action='store_true',
                                   help='Use csv.DictReader. '
                                   '  '
                                   '  '
                                   'By default, CSVs will be read line by line,  '
                                   'using the standard csv.reader().  '
                                   '  '
                                   'This will enable [csv.DictReader()](https://docs.python.org/3/library/csv.html#csv.DictReader),  '
                                   'which allows to access CSV fields by name in mappings.  '
                                   '  '
                                   'A CSV with a header is required for this setting to work.  '
                                   '  '
                                   'Note that `csv.DictReader()` may be slower than the default `csv.reader()`.')
        settings_args.add_argument("--recursive_load",
                                   action='store_true', default=False,
                                   help='Recursive local sub dirs. '
                                   '  '
                                   '  '
                                   'If set, process input directories '
                                   'recursively (default depth: `2`)')
        settings_args.add_argument("--skip_until_file",
                                   help='Skip until file x. '
                                   '  '
                                   '  '
                                   'If local input, skip all files '
                                   'until file with name `x` appears '
                                   '(default: start immediately)',
                                   type=str)
        settings_args.add_argument("--skip_until_record",
                                   help='Skip until record x. '
                                   '  '
                                   '  '
                                   'If local input, skip all records '
                                   'until record `x` '
                                   '(default: start with first)',
                                   type=int)
        settings_args.add_argument("--zip_records",
                                   action='store_true', default=False,
                                   help='Zip records parallel. '
                                   '  '
                                   '  '
                                   '* Use this flag to zip records of '
                                   'multiple input files  '
                                   '* e.g. `List1[A,B,C]`, `List2[1,2,3]` will be '
                                   'combined (zipped) on read to '
                                   '`List[A1,B2,C3]`  ')
        settings_args.add_argument("--min_geoaccuracy",
                                   help='Min geoaccuracy to use '
                                   '  '
                                   '  '
                                   'Set to `latlng`, `place`, '
                                   'or `city` to limit processing of records based '
                                   'on mininum geoaccuracy (default: no limit)',
                                   type=str)
        settings_args.add_argument("--include_lbsn_objects",
                                   help='lbsn objects to process '
                                   '  '
                                   '  '
                                   'If processing from lbsn db (`rawdb`), '
                                   'provide a comma separated list '
                                   'of [lbsn objects][1] to include. '
                                   '  '
                                   'May contain:  '
                                   '* origin  '
                                   '* country  '
                                   '* city  '
                                   '* place  '
                                   '* user_groups  '
                                   '* user  '
                                   '* post  '
                                   '* post_reaction  '
                                   '  '
                                   'Notes:  '
                                   '* Excluded objects will not be queried, but empty '
                                   'objects may be created due to referenced '
                                   'foreign key relationships.  '
                                   '* Defaults to '
                                   '`origin,post`  '
                                   '[1]: https://lbsn.vgiscience.org/structure/',
                                   type=str)
        settings_args.add_argument("--include_lbsn_bases",
                                   help='lbsn bases to update '
                                   '  '
                                   '  '
                                   'If the target output type is `hll`, '
                                   'provide a comma separated list '
                                   'of lbsn bases to include/update/store to. '
                                   '  '
                                   '  '
                                   'Currently supported:  '
                                   '* hashtag  '
                                   '* emoji  '
                                   '* term  '
                                   '* _hashtag_latlng  '
                                   '* _term_latlng  '
                                   '* _emoji_latlng  '
                                   '* _month_hashtag  '
                                   '* _month_latlng  '
                                   '* monthofyear  '
                                   '* month  '
                                   '* dayofmonth  '
                                   '* dayofweek  '
                                   '* hourofday  '
                                   '* year  '
                                   '* month  '
                                   '* date  '
                                   '* timestamp  '
                                   '* country  '
                                   '* region  '
                                   '* city  '
                                   '* place  '
                                   '* latlng  '
                                   '* community  '
                                   '  '
                                   'Bases not included will be skipped. Per '
                                   'default, **no bases** will be considered. '
                                   '  '
                                   'Example:  '
                                   '```bash'
                                   '--include_lbsn_bases hashtag,place,date,community  '
                                   '```'
                                   'Argument only allowed one time.',
                                   type=str)
        settings_args.add_argument("--override_lbsn_query_schema",
                                   help='Override schema and table name '
                                   '  '
                                   '  '
                                   'This can be used to redirect lbsn queries on '
                                   'the given object from input db to a specific schema/table '
                                   'such as a materialized view. '
                                   '  '
                                   '  '
                                   'This can be usefull (e.g.) to limit '
                                   'processing of input data to a specific '
                                   'query.  '
                                   '  '
                                   'Format is `lbsn_type,schema.table`.  '
                                   '  '
                                   'Example:  '
                                   '```bash'
                                   '--override_lbsn_query_schema post,mviews.mypostquery  '
                                   '```'
                                   'Argument can be used multiple times.',
                                   action='append',
                                   type=str)
        settings_args.add_argument("--hmac_key",
                                   help='Override db hmac key '
                                   '  '
                                   '  '
                                   'The hmac key that is used for cryptographic hashing '
                                   'during creation of HLL sets. Override what is '
                                   'set in hllworker database here. '
                                   '  '
                                   '  '
                                   'Remember to re-use the same hmac key for any '
                                   'consecutive update of HLL sets. '
                                   '  '
                                   '  '
                                   'The crypt.salt variable can also be set (temporarily or permanently) in the '
                                   'hll worker database itself. '
                                   '  '
                                   'Example:  '
                                   '```sql'
                                   'ALTER DATABASE hllworkerdb SET crypt.salt = \'CRYPTSALT\';  '
                                   '```'
                                   '  '
                                   '  '
                                   'Further information is available in the [YFCC HLL tutorial][2]. '
                                   '  '
                                   '[2]: https://lbsn.vgiscience.org/tutorial/yfcc-geohash/#prepare-query-and-cryptographic-hashing',
                                   action='append',
                                   type=str)
        return parser

    def parse_args(self, args: List = None):
        """Process input *args

        Arguments:
            args: Optional prepopulated list of args. Can be used to define
            and extend arguments outside of lbsntransform
        """

        parser = BaseConfig.get_arg_parser()
        args = parser.parse_args(args)
        if args.file_input:
            self.is_local_input = True
            self.local_file_type = args.file_type
            if args.is_stacked_json:
                self.is_stacked_json = True
            if args.is_line_separated_json:
                self.is_line_separated_json = True
            if not args.input_path_url:
                self.input_path = Path.cwd() / "01_Input"
                print(f'Using Path: {self.input_path}')
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
        if args.dry_run:
            self.dry_run = True
        if args.csv_output:
            raise NotImplementedError(
                "CSV output is currently not available.")
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
        if not self.csv_output and args.dbuser_output:
            self.dbuser_output = args.dbuser_output
            self.dbpassword_output = args.dbpassword_output
            output_ip, output_port = BaseConfig.get_ip_port(
                args.dbserveraddress_output)
            self.dbserveraddress_output = output_ip
            if output_port:
                self.dbserverport_output = output_port
            self.dbname_output = args.dbname_output
        if not self.csv_output and args.dbformat_output:
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
            # hack: converts to int (row-count) if possible
            # otherwise uses str (row-id lookup)
            # TODO: separate into different cli args
            self.startwith_db_rownumber = self.int_or_str(
                args.startwith_db_rownumber)
        if args.endwith_db_rownumber:
            self.endwith_db_rownumber = args.endwith_db_rownumber
        if args.debug_mode:
            self.debug_mode = args.debug_mode
        if args.input_lbsn_type:
            self.input_lbsn_type = args.input_lbsn_type
        if args.map_full_relations:
            self.map_relations = True
        if args.csv_allow_linebreaks:
            self.csv_suppress_linebreaks = False
        if args.csv_delimiter:
            self.csv_delim = args.csv_delimiter
        if args.use_csv_dictreader:
            self.use_csv_dictreader = args.use_csv_dictreader
        if args.recursive_load:
            self.recursive_load = True
        if args.skip_until_file:
            self.skip_until_file = args.skip_until_file
        if args.zip_records:
            self.zip_records = True
        if args.skip_until_record:
            self.skip_until_record = args.skip_until_record
        if args.mappings_path:
            self.mappings_path = Path(args.mappings_path)
        if args.min_geoaccuracy:
            self.min_geoaccuracy = self.check_geoaccuracy_input(
                args.min_geoaccuracy)
        if args.include_lbsn_objects:
            self.include_lbsn_objects = \
                args.include_lbsn_objects.lower().split(",")
        else:
            self.include_lbsn_objects = ['origin,post']
        if args.include_lbsn_bases:
            self.include_lbsn_bases = args.include_lbsn_bases.split(",")
        if args.override_lbsn_query_schema:
            self.override_lbsn_query_schema = self.compile_schema_override(
                args.override_lbsn_query_schema)
        if args.hmac_key:
            self.hmac_key = args.hmac_key

    @classmethod
    def compile_schema_override(
            cls, override_lbsn_query_schema: List[str]) -> List[Tuple[str, str]]:
        """Split lbsn_type from schema.table override"""
        lbsn_query_schema = []
        for override in override_lbsn_query_schema:
            try:
                lbsn_type, schema_table_override = override.split(
                    ",")
            except ValueError as e:
                raise ValueError(
                    f"Cannot split lbsn_type from schema.table ({override}). "
                    f"Make sure override_lbsn_query_schema entries are "
                    f"formatted correctly, e.g. lbsn_type,schema.table") from e
            lbsn_query_schema.append(
                (lbsn_type.lower(), schema_table_override.lower()))
        return lbsn_query_schema

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

    @classmethod
    def int_or_str(cls, value_str: str):
        """Returns int if value is of type int, otherwise str"""
        try:
            return int(value_str)
        except:
            return value_str
