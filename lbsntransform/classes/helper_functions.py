# -*- coding: utf-8 -*-

"""
Collection of helper functions being used in lbsntransform package.
"""


import csv
import datetime as dt
import logging
import re
import sys
import time
from typing import Tuple, Any, Iterator
from datetime import timezone
import json
from json import JSONDecodeError, JSONDecoder

import emoji
from google.protobuf.timestamp_pb2 import Timestamp
from lbsnstructure.lbsnstructure_pb2 import (CompositeKey, RelationshipKey,
                                             City, Country, Place,
                                             Post, PostReaction,
                                             Relationship, User,
                                             UserGroup)
from shapely import geos, wkt

# due to different protocol buffers implementations on Unix, MacOS and Windows
# import types based on OS
import platform
PLATFORM_SYS = platform.system()
if PLATFORM_SYS == 'Linux':
    from google.protobuf.pyext._message import RepeatedCompositeContainer  # pylint: disable=no-name-in-module
    from google.protobuf.pyext._message import ScalarMapContainer  # pylint: disable=no-name-in-module
else:
    from google.protobuf.internal.containers import RepeatedCompositeFieldContainer  # pylint: disable=no-name-in-module
    from google.protobuf.internal.containers import ScalarMapContainer  # pylint: disable=no-name-in-module

# pylint: disable=no-member


class HelperFunctions():

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
                HelperFunctions._log_JSONDecodeError(gen)
                pass
            except Exception as e:
                HelperFunctions._log_unhandled_exception(e)
                pass

    @staticmethod
    def json_load_wrapper(gen, single: bool = None):
        """Wraps json load(s) and catches any error"""
        if single is None:
            single = False
        try:
            if single:
                record = json.loads(gen)
                return record
            else:
                records = json.load(gen)
                return records
        except json.decoder.JSONDecodeError:
            HelperFunctions._log_JSONDecodeError(gen)
            pass
        except Exception as e:
            HelperFunctions._log_unhandled_exception(e)
            pass

    @staticmethod
    def _log_JSONDecodeError(record_str: str):
        logging.getLogger('__main__').warning(
            f"\nJSONDecodeError: skipping entry\n{record_str}\n\n")

    @staticmethod
    def _log_unhandled_exception(e: str):
        logging.getLogger('__main__').warning(
            f"\nUnhandled exception: \n{e}\n ..skipping entry\n")

    @staticmethod
    def report_stats(input_cnt, current_cnt, lbsn_records):
        """Format string for reporting stats."""
        report_stats = (f'{input_cnt} '
                        f'input records processed (up to '
                        f'{current_cnt}). '
                        f'{HelperFunctions.get_count_stats(lbsn_records)}')
        return report_stats

    @staticmethod
    def get_count_stats(lbsn_records):
        """Format string for reporting count stats."""
        report_stats = (
            f'Count per type: '
            f'{lbsn_records.get_type_counts()}'
            f'records.')
        return report_stats

    @staticmethod
    def get_str_formatted_today():
        """Returns date as string (YYYY-mm-dd)"""
        today = dt.date.today()
        today_str = today.strftime("%Y-%m-%d")
        return today_str

    @staticmethod
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

    @staticmethod
    def geoacc_within_threshold(post_geoaccuracy, min_geoaccuracy):
        """Checks if geoaccuracy is within or below threshhold defined"""
        if min_geoaccuracy == Post.LATLNG:
            allowed_geoaccuracies = [Post.LATLNG]
        elif min_geoaccuracy == Post.PLACE:
            allowed_geoaccuracies = [Post.LATLNG, Post.PLACE]
        elif min_geoaccuracy == Post.CITY:
            allowed_geoaccuracies = [Post.LATLNG, Post.PLACE,
                                     Post.CITY]
        else:
            return True
        # check post geoaccuracy
        if post_geoaccuracy in allowed_geoaccuracies:
            return True
        else:
            return False

    @staticmethod
    def get_version():
        """Gets the program version number from version file in root"""
        with open('VERSION') as version_file:
            version_var = version_file.read().strip()
        return version_var

    @staticmethod
    def log_main_debug(debug_text):
        """Issues a main debug log in case it is
        needed for static functions.
        """
        logging.getLogger('__main__').debug(debug_text)

    @staticmethod
    def null_notice(x):
        """Reporting: Suppresses null notice (for Null island)
        if value is zero.
        """
        def null_notice_x(x): return f'(Null Island: {x})' if x > 0 else ''
        return null_notice_x(x)

    @staticmethod
    def utc_to_local(utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    @staticmethod
    def extract_emoji(str):
        # str = str.decode('utf-32').encode('utf-32', 'surrogatepass')
        # return list(c for c in str if c in emoji.UNICODE_EMOJI)
        return list(c for c in str if c in emoji.UNICODE_EMOJI)

    @staticmethod
    def get_rectangle_bounds(points):
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
            # initializes new record with composite ID
        c_key = CompositeKey()
        c_key.origin.CopyFrom(origin)
        c_key.id = id
        record.pkey.CopyFrom(c_key)
        return record

    @staticmethod
    def new_lbsn_relation_with_id(lbsn_relationship,
                                  relation_to_id,
                                  relation_from_id,
                                  relation_origin):
        # initializes new relationship with 2 composite IDs for one origin
        c_key_to = CompositeKey()
        c_key_to.origin.CopyFrom(relation_origin)
        c_key_to.id = relation_to_id
        c_key_from = CompositeKey()
        c_key_from.origin.CopyFrom(relation_origin)
        c_key_from.id = relation_from_id
        r_key = RelationshipKey()
        r_key.relation_to.CopyFrom(c_key_to)
        r_key.relation_from.CopyFrom(c_key_from)
        lbsn_relationship.pkey.CopyFrom(r_key)
        return lbsn_relationship

    @staticmethod
    def is_post_reaction(jsonString):
        if 'quoted_status' in jsonString \
                or 'retweeted_status' in jsonString \
                or jsonString.get('in_reply_to_status_id_str'):
            # The retweeted field will return true if a tweet _got_ retweeted
            # To detect if a tweet is a retweet of other tweet,
            # check the retweeted_status field
            return True
        else:
            return False

    @staticmethod
    def assign_media_post_type(json_media_string):
        """Media type assignment based on Twitter json"""
        # if post, get type of first entity
        type_string = json_media_string[0].get('type')
        # type is either photo, video, or animated_gif
        # https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/extended-entities-object.html
        if type_string:
            if type_string == "photo":
                post_type = Post.IMAGE
            elif type_string in ("video", "animated_gif"):
                post_type = Post.VIDEO

        else:
            post_type = Post.OTHER
            logging.getLogger('__main__').debug(f'Other Post type detected: '
                                                f'{json_media_string}')
        return post_type

    @staticmethod
    def json_date_string_to_proto(json_date_string):
        # Parse String -Timestamp Format found in Twitter json
        date_time_record = dt.datetime.strptime(json_date_string,
                                                '%a %b %d %H:%M:%S +0000 %Y')
        protobuf_timestamp_record = Timestamp()
        # Convert to ProtoBuf Timestamp Recommendation
        protobuf_timestamp_record.FromDatetime(date_time_record)
        return protobuf_timestamp_record

    @staticmethod
    def json_date_timestamp_to_proto(json_date_timestamp):
        # Parse String -Timestamp Format found in Twitter json
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
            t_format = '%m/%d/%Y %H:%M:%S'
        try:
            date_time_record = dt.datetime.strptime(
                csv_datestring, t_format)
        except ValueError:
            return None
        protobuf_timestamp_record = Timestamp()
        # Convert to ProtoBuf Timestamp Recommendation
        protobuf_timestamp_record.FromDatetime(date_time_record)
        return protobuf_timestamp_record

    @staticmethod
    def parse_timestamp_string_to_protobuf(timestamp_string):
        """Converts timestamp string to protobuf object"""
        # Parse from RFC 3339 date string to Timestamp.
        time_date = dt.datetime.fromtimestamp(int(timestamp_string))
        protobuf_timestamp_record = Timestamp()
        protobuf_timestamp_record.FromDatetime(time_date)
        return protobuf_timestamp_record

    @staticmethod
    def get_mentioned_users(userMentions_jsonString, origin):
        mentioned_users_list = []
        for user_mention in userMentions_jsonString:  # iterate over the list
            ref_user_record = \
                HelperFunctions.new_lbsn_record_with_id(User(),
                                                        user_mention.get(
                                                        'id_str'),
                                                        origin)
            ref_user_record.user_fullname = \
                user_mention.get('name')  # Needs to be saved
            ref_user_record.user_name = user_mention.get('screen_name')
            mentioned_users_list.append(ref_user_record)
        return mentioned_users_list

    @staticmethod
    def substitute_referenced_user(main_post, origin, log):
        # Look for mentioned userRecords
        ref_user_pkey = None
        user_mentions_json = main_post.get('entities').get('user_mentions')
        if user_mentions_json:
            ref_user_records = \
                HelperFunctions.get_mentioned_users(user_mentions_json,
                                                    origin)
            # if it is a retweet, and the status contains 'RT @',
            # and the mentioned UserID is also in the status,
            # we can almost be completely certain that it is the userid who
            # posted the original tweet that was retweeted
            if ref_user_records \
               and ref_user_records[0].user_name.lower() in \
               main_post.get('text').lower() \
               and main_post.get('text').startswith(f'RT @'):
                ref_user_pkey = ref_user_records[0].pkey
            if ref_user_pkey is None:
                log.warning(
                    f'No User record found for referenced post in: '
                    f'{main_post}')
                input("Press Enter to continue... "
                      "(post will be saved without userid)")
        return ref_user_pkey

    @staticmethod
    def null_check(record_attr):
        """Helper function to check for Null Values
        """
        if not record_attr:
            # will catch empty and None
            return None
        # This function will also remove Null bytes from string,
        # which aren't supported by Postgres
        if isinstance(record_attr, str):
            record_attr = HelperFunctions.clean_null_bytes_from_str(
                record_attr)
        return record_attr

    @staticmethod
    def null_geom_check(geom_attr):
        """Helper function to check for Null Values
        in geometry columns and replace with Null Island

        Note:
        null_geom_check is only applied to geometry columns
        with NOT NULL Constraint
        """
        if geom_attr is None or \
                (isinstance(geom_attr, str) and geom_attr == ''):
            null_island = "POINT(%s %s)" % (0, 0)
            return null_island
        return geom_attr

    @staticmethod
    def null_check_datetime(recordAttr):
        if not recordAttr:
            # will catch empty and None
            return None
        try:
            dt_attr = recordAttr.ToDatetime()
        except:
            return None
        if dt_attr == dt.datetime(1970, 1, 1, 0, 0, 0):
            return None
        else:
            return recordAttr.ToDatetime()

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
        NOT_WHITESPACE = re.compile(r'[^\s]')
        while True:
            match = NOT_WHITESPACE.search(document, pos)
            if not match:
                return
            pos = match.start()

            try:
                obj, pos = decoder.raw_decode(document, pos)
            except JSONDecodeError:
                # do something sensible if there's some error
                raise
            yield obj

    @staticmethod
    def clean_null_bytes_from_str(str):
        str_without_null_byte = str.replace('\x00', '')
        return str_without_null_byte

    @staticmethod
    def turn_lower(str):
        """Returns lower but keeps none values"""
        if str:
            return (str.lower())
        else:
            return str

    @staticmethod
    def empty_list(list):
        """Returns lower but keeps none values"""
        if list:
            if len(list) == 0:
                return None
            else:
                return list
        else:
            return None

    @staticmethod
    def is_composite_field_container(in_obj):
        """Checks whether in_obj is of type RepeatedCompositeFieldContainer"""
        if PLATFORM_SYS == 'Linux':
            if isinstance(
                    in_obj, (RepeatedCompositeContainer, ScalarMapContainer)):
                return True
        else:
            if isinstance(
                    in_obj, (RepeatedCompositeFieldContainer, ScalarMapContainer)):
                return True
        return False

    @staticmethod
    def map_to_dict(proto_map):
        """Converts protobuf field map (ScalarMapContainer)
        to Dictionary"""
        if proto_map:
            mapped_dict = dict(zip(proto_map.keys(), proto_map.values()))
            return mapped_dict
        return {}

    @staticmethod
    def merge_existing_records(oldrecord, newrecord):
        # Basic Compare function for GUIDS
        # First check if length of both ProtoBuf Messages are the same
        old_record_string = oldrecord.SerializeToString()
        new_record_string = newrecord.SerializeToString()
        if not len(old_record_string) == len(new_record_string):
            # no need to do anything if same lengt
            oldrecord.MergeFrom(newrecord)
            # updatedrecord = self.deepCompareMergeMessages(oldrecord,
            #                                               newrecord)

    @staticmethod
    def load_importer_mapping_module(origin: int):
        """ Switch import module based on origin input
            1 - Instagram, 2 - Flickr, 3 - Twitter, 4 - Facebook
        """
        if origin == 2:
            from .field_mapping_flickr import FieldMappingFlickr as importer
        elif origin == 21:
            # Flickr YFCC100M dataset
            from .field_mapping_yfcc100m import FieldMappingYFCC100M as importer
        elif origin == 3:
            from .field_mapping_twitter import FieldMappingTwitter as importer
        elif origin == 41:
            from .field_mapping_fb import FieldMappingFBPlace as importer
        else:
            raise ValueError("Input type not supported")
        return importer

    @staticmethod
    def dict_type_switcher(desc_name):
        """ Create protoBuf messages by name
        """
        dict_switcher = {
            Country().DESCRIPTOR.name: Country(),
            City().DESCRIPTOR.name: City(),
            Place().DESCRIPTOR.name: Place(),
            User().DESCRIPTOR.name: User(),
            UserGroup().DESCRIPTOR.name:  UserGroup(),
            Post().DESCRIPTOR.name: Post(),
            PostReaction().DESCRIPTOR.name: PostReaction(),
            Relationship().DESCRIPTOR.name: Relationship()
        }
        return dict_switcher.get(desc_name)

    @staticmethod
    def check_notice_empty_post_guid(post_guid):
        if not post_guid:
            logging.getLogger('__main__').warning(f'No PostGuid\n\n'
                                                  f'{post_guid}')
            # input("Press Enter to continue... (entry will be skipped)")
            return False
        else:
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
            skipped_geo = (f'Skipped '
                           f'{skipped_geo_count} '
                           f'due to low geoaccuracy.')
        if skipped_ignorelist_count > 0:
            skipped_ignore = (f'Skipped '
                              f'{skipped_ignorelist_count} '
                              f'due to ignore list.')
        if skipped_geo is None and skipped_ignore is None:
            return ''
        else:
            report_str = ' '.join([skipped_geo, skipped_ignore])
            return report_str


class LBSNRecordDicts():
    def __init__(self):
        self.lbsn_country_dict = dict()
        self.lbsn_city_dict = dict()
        self.lbsn_place_dict = dict()
        self.lbsn_user_group_dict = dict()
        self.lbsn_user_dict = dict()
        self.lbsn_post_dict = dict()
        self.lbsn_post_reaction_dict = dict()
        self.lbsn_relationship_dict = dict()
        self.key_hashes = {Post.DESCRIPTOR.name: set(),
                           Country.DESCRIPTOR.name: set(),
                           City.DESCRIPTOR.name: set(),
                           Place.DESCRIPTOR.name: set(),
                           UserGroup.DESCRIPTOR.name: set(),
                           User.DESCRIPTOR.name: set(),
                           PostReaction.DESCRIPTOR.name: set(),
                           Relationship.DESCRIPTOR.name: set()}
        self.count_glob = 0  # total number of records added
        self.count_glob_total = 0
        self.count_dup_merge = 0  # number of duplicate records merged
        self.count_dup_merge_total = 0
        # returns all recordsDicts in correct order,
        # with names as references (tuple)
        self.all_dicts = [
            (self.lbsn_country_dict, Country().DESCRIPTOR.name),
            (self.lbsn_city_dict, City().DESCRIPTOR.name),
            (self.lbsn_place_dict, Place().DESCRIPTOR.name),
            (self.lbsn_user_group_dict, UserGroup().DESCRIPTOR.name),
            (self.lbsn_user_dict, User().DESCRIPTOR.name),
            (self.lbsn_post_dict, Post().DESCRIPTOR.name),
            (self.lbsn_post_reaction_dict, PostReaction().DESCRIPTOR.name),
            (self.lbsn_relationship_dict, Relationship().DESCRIPTOR.name)
        ]

    def get_current_count(self):
        count_glob = self.count_glob
        return count_glob

    def get_all_records(self) -> Iterator[Tuple[Any, str]]:
        """Returns tuple of 1) all records from self
        in correct order using all_dicts and 2) Type of record

        Order is: Country(), City(), Place(), UserGroup(),
        User(), Post(), PostReaction(), Relationship()
        """
        for records_dict in self.all_dicts:
            type_name = records_dict[1]
            for record in records_dict[0].values():
                yield record, type_name

    def get_type_counts(self):
        count_list = []
        for x, y in self.key_hashes.items():
            count_list.append(f'{x}: {len(y)} ')
        return ''.join(count_list)

    def update_key_hash(self, record):
        # Keep lists of pkeys for each type
        # this can be used to check for duplicates or to get a
        # total count for each type of records (Number of unique
        # Users, Countries, Places etc.)
        # in this case we assume that origin_id remains the same
        # in each program iteration!
        if record.DESCRIPTOR.name == Relationship().DESCRIPTOR.name:
            # we need the complete uuid of both entities for
            # relationships because they can span different origin_ids
            self.key_hashes[record.DESCRIPTOR.name].add(
                f'{record.pkey.relation_to.origin.origin_id}'
                f'{record.pkey.relation_to.id}'
                f'{record.pkey.relation_from.origin.origin_id}'
                f'{record.pkey.relation_from.id}'
                f'{record.relationship_type}')
        else:
            # all other entities can be globally uniquely
            # identified by their local guid
            self.key_hashes[record.DESCRIPTOR.name].add(record.pkey.id)

    def clear(self):
        """Clears all records from all dicts
        """
        for lbsn_dict, __ in self.all_dicts:
            lbsn_dict.clear()
        self.count_glob_total += self.count_glob
        self.count_glob = 0
        self.count_dup_merge_total += self.count_dup_merge
        self.count_dup_merge = 0

    def deep_compare_merge_messages(self, old_record, new_record):
        # Do a deep compare
        # ProtoBuf MergeFrom does a fine job
        # only problem is it concatenates repeate strings,
        # which may result in duplicate entries
        # we take care of this prior to submission (see submitData classes)
        old_record.MergeFrom(new_record)
        # for descriptor in oldRecord.DESCRIPTOR.fields:
        #        if descriptor.label == descriptor.LABEL_REPEATED:
        #            if value_old == value_new:
        #                return oldRecord
        #            elif not value_old:
        #                newEntries = value_new
        #            else:
        #                # only add difference (e.g. = new values)
        #                newEntries = list(set(value_new) - set(value_old))
        #            x = getattr(oldRecord, descriptor.name)
        #            x.extend(newEntries)
        return old_record

    def add_records_to_dict(self, records):
        if not records:
            return
        elif isinstance(records, (list,)):
            for record in records:
                self.add_record_to_dict(record)
        else:
            record = records
            self.add_record_to_dict(record)

    def dict_selector(self, record):
        """ Get dictionary by type name
        """
        dict_switcher = {
            Post().DESCRIPTOR.name: self.lbsn_post_dict,
            Country().DESCRIPTOR.name: self.lbsn_country_dict,
            City().DESCRIPTOR.name: self.lbsn_city_dict,
            Place().DESCRIPTOR.name: self.lbsn_place_dict,
            PostReaction().DESCRIPTOR.name: self.lbsn_post_reaction_dict,
            User().DESCRIPTOR.name: self.lbsn_user_dict,
            UserGroup().DESCRIPTOR.name: self.lbsn_user_group_dict
        }
        return dict_switcher.get(record.DESCRIPTOR.name)

    def add_record_to_dict(self, newrecord):
        sel_dict = self.dict_selector(newrecord)
        pkeyID = newrecord.pkey.id
        if newrecord.pkey.id in sel_dict:
            oldrecord = sel_dict[pkeyID]
            # oldrecord will be modified/updated
            HelperFunctions.merge_existing_records(oldrecord, newrecord)
            self.count_dup_merge += 1
        else:
            # just count new entries
            self.count_glob += 1
            # update keyHash only necessary for new record
            self.update_key_hash(newrecord)
            sel_dict[pkeyID] = newrecord

    def add_relationship_to_dict(self, newrelationship):
        pkey_id = f'{newrelationship.pkey.relation_to.origin.origin_id}' \
                  f'{newrelationship.pkey.relation_to.id}' \
                  f'{newrelationship.pkey.relation_from.origin.origin_id}' \
                  f'{newrelationship.pkey.relation_from.id}' \
                  f'{newrelationship.relationship_type}'
        if pkey_id not in self.lbsn_relationship_dict:
            self.count_progress_report()
            self.lbsn_relationship_dict[pkey_id] = newrelationship
            # update keyHash only necessary for new record
            self.update_key_hash(newrelationship)


class GeocodeLocations():
    """Class for geocoding of text to lat/lng values.
    """

    def __init__(self):
        self.geocode_dict = dict()

    def load_geocodelist(self, file):
        # read each unsorted file and sort lines based on datetime (as string)
        with open(file, newline='', encoding='utf8') as f:
            # next(f) #Skip Headerrow
            locationfile_list = csv.reader(
                f, delimiter=',', quotechar='', quoting=csv.QUOTE_NONE)
            for location_geocode in locationfile_list:
                self.geocode_dict[location_geocode[2].replace(
                    ';', ',')] = (float(location_geocode[0]),  # lat
                                  location_geocode[1])  # lng
        print(f'Loaded {len(self.geocode_dict)} geocodes.')


class TimeMonitor():
    """Utility to report processing speed

    Once initiallized, the start time will be
    recorded and can be stopped at any time with
    stop_time(), which will return the time passed
    in a text readable time format.
    """

    def __init__(self):
        self.now = time.time()

    def stop_time(self):
        """Returns a text with time passed since self.now"""
        later = time.time()
        hours, rem = divmod(later-self.now, 3600)
        minutes, seconds = divmod(rem, 60)
        # difference = int(later - self.now)
        report_msg = f'{int(hours):0>2} Hours {int(minutes):0>2} ' \
                     f'Minutes and {seconds:05.2f} Seconds passed.'
        return report_msg
