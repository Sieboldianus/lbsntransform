# -*- coding: utf-8 -*-

"""
Shared structural classes
"""

import time
import csv
from typing import Any, Iterator, Tuple
from lbsnstructure import lbsnstructure_pb2 as lbsn


class Coordinates():
    """Lat lng coordinates in Decimal Degrees WGS1984"""

    def __init__(self, lat=None, lng=None):
        if lat is None:
            lat = 0
        if lng is None:
            lng = 0
        self.lat: float = self.lat_within_range(lat)
        self.lng: float = self.lng_within_range(lng)

    @classmethod
    def lat_within_range(cls, lat):
        if not -90 <= lat <= 90:
            raise ValueError('Latitude outside allowed range')
        return lat

    @classmethod
    def lng_within_range(cls, lng):
        if not -180 <= lng <= 180:
            raise ValueError('Longitude outside allowed range')
        return lng


class LBSNRecordDicts():
    """Parent structure to store collected lbsnstructures"""

    def __init__(self):
        self.lbsn_origin_dict = dict()
        self.lbsn_country_dict = dict()
        self.lbsn_city_dict = dict()
        self.lbsn_place_dict = dict()
        self.lbsn_user_group_dict = dict()
        self.lbsn_user_dict = dict()
        self.lbsn_post_dict = dict()
        self.lbsn_post_reaction_dict = dict()
        self.lbsn_relationship_dict = dict()
        self.key_hashes = {lbsn.Origin.DESCRIPTOR.name: set(),
                           lbsn.Post.DESCRIPTOR.name: set(),
                           lbsn.Country.DESCRIPTOR.name: set(),
                           lbsn.City.DESCRIPTOR.name: set(),
                           lbsn.Place.DESCRIPTOR.name: set(),
                           lbsn.UserGroup.DESCRIPTOR.name: set(),
                           lbsn.User.DESCRIPTOR.name: set(),
                           lbsn.PostReaction.DESCRIPTOR.name: set(),
                           lbsn.Relationship.DESCRIPTOR.name: set()}
        self.count_glob = 0  # total number of records added
        self.count_glob_total = 0
        self.count_dup_merge = 0  # number of duplicate records merged
        self.count_dup_merge_total = 0
        # returns all recordsDicts in correct order,
        # with names as references (tuple)
        self.all_dicts = [
            (self.lbsn_origin_dict, lbsn.Origin().DESCRIPTOR.name),
            (self.lbsn_country_dict, lbsn.Country().DESCRIPTOR.name),
            (self.lbsn_city_dict, lbsn.City().DESCRIPTOR.name),
            (self.lbsn_place_dict, lbsn.Place().DESCRIPTOR.name),
            (self.lbsn_user_group_dict, lbsn.UserGroup().DESCRIPTOR.name),
            (self.lbsn_user_dict, lbsn.User().DESCRIPTOR.name),
            (self.lbsn_post_dict, lbsn.Post().DESCRIPTOR.name),
            (self.lbsn_post_reaction_dict, lbsn.PostReaction().DESCRIPTOR.name),
            (self.lbsn_relationship_dict, lbsn.Relationship().DESCRIPTOR.name)
        ]

    def get_current_count(self):
        """Return count of collected records"""
        count_glob = self.count_glob
        return count_glob

    def get_all_records(self) -> Iterator[Tuple[Any, str]]:
        """Returns tuple of 1) all records from self
        in correct order using all_dicts and 2) Type of record

        Order is: lbsn.Country(), lbsn.City(), lbsn.Place(), lbsn.UserGroup(),
        lbsn.User(), lbsn.Post(), lbsn.PostReaction(), lbsn.Relationship()
        """
        for records_dict in self.all_dicts:
            type_name = records_dict[1]
            for record in records_dict[0].values():
                yield record, type_name

    def get_type_counts(self):
        """Get record counts per lbsn type"""
        count_list = []
        for x, y in self.key_hashes.items():
            count_list.append(f'{x}: {len(y)} ')
        return ''.join(count_list)

    def update_key_hash(self, record, key=None):
        """Update key-hash with record

        Keep lists of pkeys for each type
        this can be used to check for duplicates or to get a
        total count for each type of records (Number of unique
        Users, Countries, Places etc.)
        in this case we assume that origin_id remains the same
        in each program iteration!
        """
        if key is not None:
            self.key_hashes[record.DESCRIPTOR.name].add(key)
            return
        if record.DESCRIPTOR.name == lbsn.Relationship().DESCRIPTOR.name:
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
        """Do a deep compare & merge of two lbsn records

        ProtoBuf MergeFrom does a fine job
        only problem is it concatenates repeate strings,
        which may result in duplicate entries
        we take care of this prior to submission (see submitData classes)
        """
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
        """Add single or multiple lbsnrecords to dicts"""
        if not records:
            return
        if isinstance(records, (list,)):
            for record in records:
                self.add_record_to_dict(record)
        else:
            record = records
            self.add_record_to_dict(record)

    def dict_selector(self, record):
        """ Get dictionary by record type name"""
        dict_switcher = {
            lbsn.Post().DESCRIPTOR.name: self.lbsn_post_dict,
            lbsn.Country().DESCRIPTOR.name: self.lbsn_country_dict,
            lbsn.City().DESCRIPTOR.name: self.lbsn_city_dict,
            lbsn.Place().DESCRIPTOR.name: self.lbsn_place_dict,
            lbsn.PostReaction().DESCRIPTOR.name: self.lbsn_post_reaction_dict,
            lbsn.User().DESCRIPTOR.name: self.lbsn_user_dict,
            lbsn.UserGroup().DESCRIPTOR.name: self.lbsn_user_group_dict,
            lbsn.Origin().DESCRIPTOR.name: self.lbsn_origin_dict
        }
        return dict_switcher.get(record.DESCRIPTOR.name)

    def add_record_to_dict(self, newrecord):
        """Add single lbsn record to dict"""
        sel_dict = self.dict_selector(newrecord)
        try:
            pkey_id = newrecord.pkey.id
        except AttributeError:
            # inexpensive try that is raised rarely
            # lbsn origins have no composite pkey
            # use origin_id instead
            pkey_id = newrecord.origin_id
        if pkey_id in sel_dict:
            oldrecord = sel_dict[pkey_id]
            # oldrecord will be modified/updated
            self.merge_existing_records(oldrecord, newrecord)
            self.count_dup_merge += 1
        else:
            # just count new entries
            self.count_glob += 1
            # update keyHash only necessary for new record
            self.update_key_hash(newrecord, pkey_id)
            sel_dict[pkey_id] = newrecord

    def add_relationship_to_dict(self, newrelationship):
        """Add single lbsn relationship to dict"""
        pkey_id = f'{newrelationship.pkey.relation_to.origin.origin_id}' \
                  f'{newrelationship.pkey.relation_to.id}' \
                  f'{newrelationship.pkey.relation_from.origin.origin_id}' \
                  f'{newrelationship.pkey.relation_from.id}' \
                  f'{newrelationship.relationship_type}'
        if pkey_id not in self.lbsn_relationship_dict:
            # self.count_progress_report()
            self.lbsn_relationship_dict[pkey_id] = newrelationship
            # update keyHash only necessary for new record
            self.update_key_hash(newrelationship)

    @classmethod
    def merge_existing_records(cls, oldrecord, newrecord):
        """Merge two lbsn records

        Basic Compare function for GUIDS
        First check if length of both ProtoBuf Messages are the same
        """
        old_record_string = oldrecord.SerializeToString()
        new_record_string = newrecord.SerializeToString()
        if not len(old_record_string) == len(new_record_string):
            # no need to do anything if same lengt
            oldrecord.MergeFrom(newrecord)
            # updatedrecord = self.deepCompareMergeMessages(oldrecord,
            #                                               newrecord)


class GeocodeLocations():
    """Class for geocoding of text to lat/lng values"""

    def __init__(self):
        self.geocode_dict = dict()

    def load_geocodelist(self, file):
        # read each unsorted file and sort lines based on datetime (as string)
        with open(file, newline='', encoding='utf8') as fhandle:
            # next(f) #Skip Headerrow
            locationfile_list = csv.reader(
                fhandle, delimiter=',', quotechar='', quoting=csv.QUOTE_NONE)
            for location_geocode in locationfile_list:
                self.geocode_dict[location_geocode[2].replace(
                    ';', ',')] = (float(location_geocode[0]),  # lat
                                  location_geocode[1])  # lng
        print(f'Loaded {len(self.geocode_dict)} geocodes.')


class TimeMonitor():
    """Utility to report processing speed

    Once initialized, the start time will be
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
