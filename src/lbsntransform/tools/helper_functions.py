# -*- coding: utf-8 -*-

"""
Collection of helper functions being used in lbsntransform package.
"""


import datetime as dt
import importlib.util
import json
import logging
import re
import string
from datetime import timezone
from json import JSONDecodeError, JSONDecoder
from pathlib import Path
from typing import List, Optional, Set, Union, Any, Dict

import lbsnstructure as lbsn
from emoji import distinct_emoji_list
from google.protobuf.timestamp_pb2 import Timestamp
from shapely import geos, wkt
from shapely.geometry import Point, Polygon

from lbsntransform.output.shared_structure import Coordinates

NLTK_AVAIL = None
STOPWORDS = None
try:
    # check if nltk is installed
    import nltk

    NLTK_AVAIL = True
except ImportError:
    pass

if NLTK_AVAIL:
    try:
        # check if stopwords corpus is available
        from nltk.corpus import stopwords

        STOPWORDS = stopwords.words("english")
    except LookupError:
        print(
            "Please use "
            "`python -c 'import nltk;nltk.download(\"stopwords\")'` "
            "to install stopwords resource globally. Continuing without "
            "nltk stopwords filter.."
        )
        STOPWORDS = None
# pylint: disable=no-member


class HelperFunctions:
    """Collection of helper functions being used in lbsntransform package"""

    # Null Geometry String (4326)
    # for improving performance in PostGIS Upserts
    NULL_GEOM_HEX = "0101000020E610000000000000000000000000000000000000"

    @staticmethod
    def value_count(value_x: str):
        """Turn none values into 0, otherwise return value"""
        if value_x is None:
            return 0
        if isinstance(value_x, int):
            return value_x
        return int(value_x) if value_x.isdigit() else 0

    @staticmethod
    def remove_prefix(text_str: str, prefix: str):
        """Remove prefix from string"""
        if text_str.startswith(prefix):
            return text_str[len(prefix) :]
        return text_str

    @staticmethod
    def concat_values_str(sql_escaped_values_list: List[str]) -> str:
        """Concat List of sql escaped values with comma separated"""
        values_str = ",".join(sql_escaped_values_list)
        return values_str

    @staticmethod
    def sanitize_string(str_text: str):
        """Sanitize text strings for postgres sql compatibility

        * remove any NUL (0x00) characters
        """
        return str_text.replace("\x00", "")

    @staticmethod
    def format_base_repr(base):
        """Return formatted string of base"""
        return (
            f"{base.NAME.base}\nFacet: {base.NAME.facet}, "
            f"Key: {base.get_key_value()}, "
            f"Metrics: \n"
            f'{[":".join([k, str(len(v))]) for k, v in base.metrics.items()]}'
        )

    @staticmethod
    def remove_hyperlinks(text_s):
        """Remove any hyperlinks from string (regex)

        Note:
        - anything between <a>xxx</a> will be kept
        """
        pattern = r"<(a|/a).*?>"
        result = re.sub(pattern, "", text_s)
        return result

    @staticmethod
    def get_all_post_terms(record: Optional[lbsn.Post] = None) -> Set[str]:
        """Returns all post terms combined in single set"""
        body_terms = HelperFunctions.select_terms(record.post_body)
        title_terms = HelperFunctions.select_terms(record.post_title)
        tag_terms = HelperFunctions.filter_terms(record.hashtags)
        all_post_terms = set.union(body_terms, title_terms, tag_terms)
        return all_post_terms

    @staticmethod
    def select_terms(text_s: str, selection_list: List[str] = None) -> Set[str]:
        """Extract list of words from sentence and return filtered version"""
        # first remove hyperlinks
        text_s = HelperFunctions.remove_hyperlinks(text_s)
        # remove problematic characters from string
        text_s = HelperFunctions.sanitize_string(text_s)
        # remove punctuation
        text_s = text_s.translate(str.maketrans("", "", string.punctuation))
        # split string by space character into list
        querywords = text_s.split()
        resultwords = HelperFunctions.filter_terms(querywords, selection_list)
        return resultwords

    @staticmethod
    def filter_terms(terms: List[str], selection_list: List[str] = None) -> Set[str]:
        """Filter a list of terms

        * based on a provided positive(negative) filter list of terms,
        * based on length (minimum 2 characters),
        * based on type (no plain numbers)
        """
        # turn lowercase
        querywords = [word.lower() for word in terms]
        # filter based on
        # - stoplist/selectionlist
        # - length (3+ character)
        # - type: no numbers
        resultwords = {
            word
            for word in querywords
            if (selection_list is None or word in selection_list)
            and len(word) > 2
            and HelperFunctions.nltk_stopword_filter(word)
            and not word.isdigit()
        }
        return resultwords

    @staticmethod
    def nltk_stopword_filter(
        term: str, nltk_avail=NLTK_AVAIL, stopwords=STOPWORDS
    ) -> bool:
        """Filter term against nltk stopwords (english)"""
        if nltk_avail is not None and stopwords is not None:
            if term in stopwords:
                return False
        return True

    @staticmethod
    def reduce_ewkt_to_wkt(geom_ewkt: str) -> str:
        """Hack to reduce extended WKT (eWKT) to WKT"""
        geom_wkt = geom_ewkt.replace("SRID=4326;", "")
        return geom_wkt

    @staticmethod
    def get_geom_from_ewkt(geom_ewkt: str) -> Union[Point, Polygon]:
        """Convert EWKT representation (without srid) to shapely geometry

        Note: either Point or Polygon
        """
        geom_wkt = HelperFunctions.reduce_ewkt_to_wkt(geom_ewkt)
        shply_geom = wkt.loads(geom_wkt)
        return shply_geom

    @staticmethod
    def get_coordinates_from_ewkt(geom: str) -> Coordinates:
        """Convert EWKT representation (with srid) to geometry

        Note:
        Shapely has no support for handling SRID (projection). The
        approach used here is a shortcut. This should be replaced
        by proper EWKT handling using a package, e.g.
        django.contrib.gis.geos or django.contrib.gis.geometry, see:
        https://docs.huihoo.com/django/1.11/ref/contrib/gis/geos.html
        """
        if not geom:
            return Coordinates()
        geom = HelperFunctions.reduce_ewkt_to_wkt(geom)
        shply_geom = HelperFunctions.get_geom_from_ewkt(geom)
        if not shply_geom.geom_type == "Point":
            raise ValueError(
                f"Expected geometry of type Point, " f"but found {shply_geom.geom_type}"
            )
        coordinates = Coordinates(
            lng=shply_geom.x, lat=shply_geom.y
        )  # pylint: disable=maybe-no-member
        return coordinates

    @staticmethod
    def extract_hashtags_from_string(text_str: str) -> Set[str]:
        """Extract hashtags with leading hash-character (#) from string

        - removes # from hashtags
        - removes duplicates
        - removes special chars (emoji etc.) from hashtags, e.g.:
            - input: "#germany🇩🇪"
            - output: [germany]
        """
        startstring = "#"
        return HelperFunctions.extract_special(text_str, startstring)

    @staticmethod
    def extract_atmentions_from_string(
        text_str: str, startstring: str = "@"
    ) -> Set[str]:
        """Extract @-mentions with leading hash-character (@) from string

        - removes @ from mentions
        - removes duplicates
        - removes special chars (emoji etc.) from mentions, e.g.:
            - input: "@userxyz🇩🇪"
            - output: [userxyz]
        - will extract users with underscore character sin name (_) but not with
          minus sign (-), since this is not allowed on Twitter
        """
        return HelperFunctions.extract_special(
            text_str, startstring, allow_underscore=True
        )

    @staticmethod
    def extract_user_mentions(
        text_str: Optional[str], startstring: str = "/u/"
    ) -> Optional[Set[str]]:
        """Extract user mentions. Default value for startstring refers to /u/ on Reddit"""
        if not text_str:
            return
        return HelperFunctions.extract_special(
            text_str, startstring, allow_minus=True, allow_underscore=True
        )

    @staticmethod
    def extract_special(
        text_str: str,
        startstring: str,
        allow_minus: bool = False,
        allow_underscore: bool = False,
    ) -> Set[str]:
        """Extract special strings based on starting character, e.g. /u/ (user mention), or #hashtags.

        allow_minus: If True, extraction for positive find will not stop at Minus-character (-).
            Usually, Minus-character is disallowed (e.g. Hashtags). But sometoimes (e.g. on Reddit
            usernames), it is allowed and needed to extract the full reference.
        allow_underscore: Same as allow_minus, just for underscore character (_)
        """
        optional_minus = ""
        optional_underscore = ""
        additional_chars = ""
        if allow_minus:
            optional_minus = "-"
        if allow_underscore:
            optional_underscore = "_"
        if allow_minus or allow_underscore:
            additional_chars = rf"[{optional_minus}{optional_underscore}]?\w+"
        extract_special_pattern = re.compile(
            rf"(?i)(?<={startstring})\w+{additional_chars}"
        )
        special_list = extract_special_pattern.findall(text_str)
        return set(special_list)

    @staticmethod
    def json_read_wrapper(gen):
        """Wraps json iterator and catches any error"""
        while True:
            try:
                yield next(gen)
            except StopIteration:
                # no further items produced by the iterator
                raise
            except json.decoder.JSONDecodeError:
                HelperFunctions._log_json_decodeerror(gen)
            except Exception as e:
                HelperFunctions._log_unhandled_exception(e)

    @staticmethod
    def json_load_wrapper(gen, single: bool = None):
        """Wraps json load(s) and catches any error"""
        if single is None:
            single = False
        try:
            if single:
                record = json.loads(gen)
                return record
            records = json.load(gen)
            return records
        except json.decoder.JSONDecodeError:
            HelperFunctions._log_json_decodeerror(gen)
        except Exception as exc_general:
            HelperFunctions._log_unhandled_exception(exc_general)

    @staticmethod
    def _log_json_decodeerror(record_str: str):
        logging.getLogger("__main__").warning(
            "\nJSONDecodeError: skipping entry\n%s\n\n", record_str
        )

    @staticmethod
    def _log_unhandled_exception(e: Any):
        logging.getLogger("__main__").warning(
            "\nUnhandled exception: \n%s\n ..skipping entry\n", e
        )

    @staticmethod
    def report_stats(input_cnt, current_cnt, lbsn_records=None):
        """Format string for reporting stats."""
        report_stats = (
            f"{input_cnt} "
            f"input records read (up to "
            f"{current_cnt}). "
            f"{HelperFunctions.get_count_stats(lbsn_records)}"
        )
        return report_stats

    @staticmethod
    def get_count_stats(lbsn_records=None):
        """Format string for reporting count stats."""
        if lbsn_records is None:
            return
        report_stats = (
            f"Count per type: " f"{lbsn_records.get_type_counts()}" f"records."
        )
        return report_stats

    @staticmethod
    def get_str_formatted_today():
        """Returns date as string (YYYY-mm-dd)"""
        today = dt.date.today()
        today_str = today.strftime("%Y-%m-%d")
        return today_str

    @staticmethod
    def set_logger():
        """Set logging handler manually,
        so we can also print to console while logging to file
        """

        logging.basicConfig(
            handlers=[logging.FileHandler("log.log", "w", "utf-8")],
            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
            level=logging.DEBUG,
        )
        log = logging.getLogger(__name__)

        # Get Stream handler
        logging.getLogger().addHandler(logging.StreamHandler())
        return log

    @staticmethod
    def geoacc_within_threshold(post_geoaccuracy, min_geoaccuracy):
        """Checks if geoaccuracy is within or below threshhold defined"""
        if min_geoaccuracy == lbsn.Post.LATLNG:
            allowed_geoaccuracies = [lbsn.Post.LATLNG]
        elif min_geoaccuracy == lbsn.Post.PLACE:
            allowed_geoaccuracies = [lbsn.Post.LATLNG, lbsn.Post.PLACE]
        elif min_geoaccuracy == lbsn.Post.CITY:
            allowed_geoaccuracies = [lbsn.Post.LATLNG, lbsn.Post.PLACE, lbsn.Post.CITY]
        else:
            return True
        # check post geoaccuracy
        return bool(post_geoaccuracy in allowed_geoaccuracies)

    @staticmethod
    def get_version():
        """Gets the program version number from version file in root"""
        with open("VERSION") as version_file:
            version_var = version_file.read().strip()
        return version_var

    @staticmethod
    def log_main_debug(debug_text):
        """Issues a main debug log in case it is
        needed for static functions.
        """
        logging.getLogger("__main__").debug(debug_text)

    @staticmethod
    def null_notice(x_value: int) -> str:
        """Reporting: Suppresses null notice (for Null island)
        if value is zero.
        """
        return f"(Null Island: {x_value})" if x_value > 0 else ""

    @staticmethod
    def utc_to_local(utc_dt):
        """Convert utc to local time"""
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    @staticmethod
    def cleanhtml(raw_html: str) -> str:
        """Remove any html tags from string"""
        cleanr = re.compile("<.*?>")
        cleantext = re.sub(cleanr, "", raw_html)
        return cleantext

    @staticmethod
    def extract_emoji(string_with_emoji: str) -> Set[str]:
        """Extract distinct set of emoji from string"""
        return distinct_emoji_list(string_with_emoji)

    @staticmethod
    def get_rectangle_bounds(points):
        """Get rectangle boundary from list of points"""
        lats = []
        lngs = []
        for point in points:
            lngs.append(point[0])
            lats.append(point[1])
        lim_y_min = min(lats)
        lim_y_max = max(lats)
        lim_x_min = min(lngs)
        lim_x_max = max(lngs)
        return lim_y_min, lim_y_max, lim_x_min, lim_x_max

    @staticmethod
    def new_lbsn_record_with_id(record, id, origin):
        """Initialize new lbsn record with composite ID"""
        c_key = lbsn.CompositeKey()
        c_key.origin.CopyFrom(origin)
        c_key.id = id
        record.pkey.CopyFrom(c_key)
        return record

    @staticmethod
    def new_lbsn_relation_with_id(
        lbsn_relationship, relation_to_id, relation_from_id, relation_origin
    ):
        """Initialize new lbsn relationship with 2 composite IDs
        for one origin
        """
        c_key_to = lbsn.CompositeKey()
        c_key_to.origin.CopyFrom(relation_origin)
        c_key_to.id = relation_to_id
        c_key_from = lbsn.CompositeKey()
        c_key_from.origin.CopyFrom(relation_origin)
        c_key_from.id = relation_from_id
        r_key = lbsn.RelationshipKey()
        r_key.relation_to.CopyFrom(c_key_to)
        r_key.relation_from.CopyFrom(c_key_from)
        lbsn_relationship.pkey.CopyFrom(r_key)
        return lbsn_relationship

    @staticmethod
    def is_post_reaction(json_string):
        """Determine if post is post reaction

        The retweeted field will return true if a tweet _got_ retweeted
        To detect if a tweet is a retweet of other tweet,
        check the retweeted_status field
        """
        return bool(
            "quoted_status" in json_string
            or "retweeted_status" in json_string
            or json_string.get("in_reply_to_status_id_str")
        )

    @staticmethod
    def assign_media_post_type(json_media_string):
        """Media type assignment based on Twitter json"""
        # if post, get type of first entity
        type_string = json_media_string[0].get("type")
        # type is either photo, video, or animated_gif
        # https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/extended-entities-object.html
        post_type = lbsn.Post.OTHER
        if type_string:
            if type_string == "photo":
                post_type = lbsn.Post.IMAGE
            elif type_string in ("video", "animated_gif"):
                post_type = lbsn.Post.VIDEO

        else:
            logging.getLogger("__main__").debug(
                "Other lbsn.Post type detected: %s", json_media_string
            )
        return post_type

    @staticmethod
    def json_date_string_to_proto(json_date_string: str):
        """Parse String -Date Format found in Twitter json"""
        date_time_record = dt.datetime.strptime(
            json_date_string, "%a %b %d %H:%M:%S +0000 %Y"
        )
        protobuf_timestamp_record = Timestamp()
        # Convert to ProtoBuf Timestamp Recommendation
        protobuf_timestamp_record.FromDatetime(date_time_record)
        return protobuf_timestamp_record

    @staticmethod
    def json_date_timestamp_to_proto(json_date_timestamp):
        """Parse String -Timestamp Format found in Twitter json"""
        date_time_record = dt.datetime.fromtimestamp(json_date_timestamp)
        protobuf_timestamp_record = Timestamp()
        # Convert to ProtoBuf Timestamp Recommendation
        protobuf_timestamp_record.FromDatetime(date_time_record)
        return protobuf_timestamp_record

    @staticmethod
    def parse_csv_datestring_to_protobuf(csv_datestring, t_format=None):
        """Parse String -Timestamp Format found in Flickr csv

        e.g. 2012-02-16 09:56:37.0
        """
        if t_format is None:
            t_format = "%m/%d/%Y %H:%M:%S"
        try:
            date_time_record = dt.datetime.strptime(csv_datestring, t_format)
        except ValueError:
            return None
        return HelperFunctions.date_to_proto(date_time_record)

    @staticmethod
    def date_to_proto(dt_record) -> Optional[Timestamp]:
        """Assign datetime to protobuf Timestamp"""
        protobuf_timestamp_record = Timestamp()
        # Convert to ProtoBuf Timestamp Recommendation
        protobuf_timestamp_record.FromDatetime(dt_record)
        return protobuf_timestamp_record

    @staticmethod
    def stringdate_to_proto(dt_string) -> Optional[Timestamp]:
        """Stringdate to proto, e.g. 2019-10-02T18:34:24"""
        protobuf_timestamp_record = Timestamp()
        protobuf_timestamp_record.FromJsonString(dt_string)
        return protobuf_timestamp_record

    @staticmethod
    def parse_timestamp_string_to_protobuf(timestamp_string):
        """Parse from RFC 3339 date string to Timestamp."""
        time_date = dt.datetime.fromtimestamp(int(timestamp_string))
        protobuf_timestamp_record = Timestamp()
        protobuf_timestamp_record.FromDatetime(time_date)
        return protobuf_timestamp_record

    @staticmethod
    def get_mentioned_users(user_mentions_json: List[Dict[str, str]], origin):
        """Return list of mentioned users from json"""
        mentioned_users_list = []
        for user_mention in user_mentions_json:  # iterate over the list
            ref_user_record = HelperFunctions.new_lbsn_record_with_id(
                lbsn.User(), user_mention.get("id_str"), origin
            )
            ref_user_record.user_fullname = user_mention.get(
                "name"
            )  # Needs to be saved
            ref_user_record.user_name = user_mention.get("screen_name")
            mentioned_users_list.append(ref_user_record)
        return mentioned_users_list

    @staticmethod
    def create_mentioned_users(mentioned_users_list_str: Set[str], origin):
        """Return list of mentioned users from json"""
        mentioned_users_list = []
        for user_mention in mentioned_users_list_str:  # iterate over the list
            ref_user_record = HelperFunctions.new_lbsn_record_with_id(
                lbsn.User(), user_mention, origin
            )
            mentioned_users_list.append(ref_user_record)
        return mentioned_users_list

    @staticmethod
    def substitute_referenced_user(main_post, origin, log):
        """Look for mentioned userRecords"""
        ref_user_pkey = None
        user_mentions_json = main_post.get("entities").get("user_mentions")
        if user_mentions_json:
            ref_user_records = HelperFunctions.get_mentioned_users(
                user_mentions_json, origin
            )
            # if it is a retweet, and the status contains 'RT @',
            # and the mentioned UserID is also in the status,
            # we can almost be completely certain that it is the userid who
            # posted the original tweet that was retweeted
            if (
                ref_user_records
                and ref_user_records[0].user_name.lower()
                in main_post.get("text").lower()
                and main_post.get("text").startswith("RT @")
            ):
                ref_user_pkey = ref_user_records[0].pkey
            if ref_user_pkey is None:
                log.warning(
                    f"No lbsn.User record found for referenced post in: " f"{main_post}"
                )
                input(
                    "Press Enter to continue... " "(post will be saved without userid)"
                )
        return ref_user_pkey

    @staticmethod
    def null_check(record_attr):
        """Helper function to check for Null Values"""
        if not record_attr:
            # will catch empty and None
            return None
        # This function will also remove Null bytes from string,
        # which aren't supported by Postgres
        if isinstance(record_attr, str):
            record_attr = HelperFunctions.clean_null_bytes_from_str(record_attr)
        return record_attr

    @staticmethod
    def null_geom_check(geom_attr):
        """Helper function to check for Null Values
        in geometry columns and replace with Null Island

        Note:
        null_geom_check is only applied to geometry columns
        with NOT NULL Constraint
        """
        if geom_attr is None or (isinstance(geom_attr, str) and geom_attr == ""):
            null_island = "POINT(0 0)"
            return null_island
        return geom_attr

    @staticmethod
    def null_check_datetime(record_attr):
        """Check if date is null or empty and replace with default value"""
        if not record_attr:
            # will catch empty and None
            return
        try:
            dt_attr = record_attr.ToDatetime()
        except:
            return
        if dt_attr == dt.datetime(1970, 1, 1, 0, 0, 0):
            return None
        return record_attr.ToDatetime()

    @staticmethod
    def return_ewkb_from_geotext(text):
        """Generates Geometry in Well-known-Text format
        from PostGis Format (e.g. 'POINT(0 0)')
        with SRID for WGS1984 (4326)

        Note that:
        geos.WKBWriter.defaults['include_srid'] = True
        must be set (see config.py)
        """
        if text is None:
            # keep Null geometries, e.g. for geom_area columns
            return None
        geom = wkt.loads(text)
        # Set SRID to WGS1984
        geos.lgeos.GEOSSetSRID(geom._geom, 4326)
        geom = geom.wkb_hex
        return geom

    @staticmethod
    def decode_stacked(document, pos=0, decoder=JSONDecoder()):
        """Decode stacked json"""
        not_whitespace = re.compile(r"[^\s]")
        while True:
            match = not_whitespace.search(document, pos)
            if not match:
                return
            pos = match.start()

            try:
                obj, pos = decoder.raw_decode(document, pos)
            except JSONDecodeError:
                raise
            yield obj

    @staticmethod
    def clean_null_bytes_from_str(text_str: str):
        """Remove null bytes from string for pg compatibility"""
        str_without_null_byte = text_str.replace("\x00", "")
        return str_without_null_byte

    @staticmethod
    def turn_lower(text_str):
        """Returns lower but keeps none values"""
        if text_str:
            return text_str.lower()
        return text_str

    @staticmethod
    def empty_list(list_str):
        """Returns lower but keeps none values"""
        if list_str:
            if len(list_str) == 0:
                return None
            else:
                return list_str
        return None

    @staticmethod
    def map_to_dict(proto_map):
        """Converts protobuf field map (ScalarMapContainer)
        to Dictionary"""
        if proto_map:
            mapped_dict = dict(zip(proto_map.keys(), proto_map.values()))
            return mapped_dict
        return {}

    @staticmethod
    def _get_file_list(path: Path, ext: str = "py"):
        """Return file list in folder"""
        return [file.stem for file in path.glob(f"*.{ext}")]

    @staticmethod
    def dynamic_get_mapping_module(origin: int, mappings_path: Path = None):
        """Function to dynamically register input mappings

        Args:
            origin: The MAPPING_ID to identify the mapping module.
            path: Override default path with user defined folder.
        """
        if mappings_path is None or origin == 0:
            mappings_module_name = "lbsntransform.input.mappings"
            from lbsntransform.input.mappings.field_mapping_lbsn import (
                importer,
            )

            return importer
        else:
            mapping_modules = HelperFunctions._get_file_list(mappings_path)
            init_file_str = "__init__"
            mappings_module_name = mappings_path.name
            for mapping_module in mapping_modules:
                if mapping_module == init_file_str:
                    continue
                spec = importlib.util.spec_from_file_location(
                    f"{mappings_path.name}.{mapping_module}",
                    mappings_path / f"{mapping_module}.py",
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "MAPPING_ID") and module.MAPPING_ID == origin:
                    if hasattr(module, "importer"):
                        importer = module.importer
                        return importer
                    raise ImportError("importer missing in {module}")
        raise ValueError(
            f"{origin} not found in {mappings_module_name}. "
            f"Input type not supported."
        )

    @staticmethod
    def load_module(package: str, name: str):
        name = f"{package}.{name}"
        __import__(name, fromlist=[""])

    @staticmethod
    def load_importer_mapping_module(origin: int, mappings_path: Path = None):
        """Switch import module based on origin input
        1 - Instagram, 2 - Flickr, 3 - Twitter, 4 - Facebook
        """
        importer = HelperFunctions.dynamic_get_mapping_module(
            origin=origin, mappings_path=mappings_path
        )
        return importer

    @staticmethod
    def dict_type_switcher(desc_name):
        """Create protoBuf messages by name"""
        dict_switcher = {
            lbsn.Country().DESCRIPTOR.name: lbsn.Country(),
            lbsn.City().DESCRIPTOR.name: lbsn.City(),
            lbsn.Place().DESCRIPTOR.name: lbsn.Place(),
            lbsn.User().DESCRIPTOR.name: lbsn.User(),
            lbsn.UserGroup().DESCRIPTOR.name: lbsn.UserGroup(),
            lbsn.Post().DESCRIPTOR.name: lbsn.Post(),
            lbsn.PostReaction().DESCRIPTOR.name: lbsn.PostReaction(),
            lbsn.Relationship().DESCRIPTOR.name: lbsn.Relationship(),
        }
        return dict_switcher.get(desc_name)

    @staticmethod
    def check_notice_empty_post_guid(post_guid):
        """Check if post_guid empty and if, raise warning"""
        if not post_guid:
            logging.getLogger("__main__").warning(f"No PostGuid\n\n" f"{post_guid}")
            return False
        return True

    @staticmethod
    def get_skipped_report(import_mapper):
        """Get count report of records skipped due to low geoaccuracy
        or ignore list"""
        skipped_geo = None
        skipped_ignore = None
        # check if methods habe been implemented in import mapper module
        try:
            skipped_geo_count = import_mapper.get_skipped_geoaccuracy()
        except AttributeError:
            skipped_geo_count = 0
        try:
            skipped_ignorelist_count = import_mapper.get_skipped_ignorelist()
        except AttributeError:
            skipped_ignorelist_count = 0
        # compile report texts
        if skipped_geo_count > 0:
            skipped_geo = f"Skipped " f"{skipped_geo_count} " f"due to low geoaccuracy."
        if skipped_ignorelist_count > 0:
            skipped_ignore = (
                f"Skipped " f"{skipped_ignorelist_count} " f"due to ignore list."
            )
        if skipped_geo is None and skipped_ignore is None:
            return ""
        else:
            report_str = " ".join(filter(None, [skipped_geo, skipped_ignore]))
            return report_str
