# -*- coding: utf-8 -*-

"""
Shared structure and mapping between HLL DB and Proto LBSN Structure.
"""

# pylint: disable=no-member

from typing import Dict, List, Tuple, Union, Iterator, Optional

from lbsnstructure import lbsnstructure_pb2 as lbsn
from lbsntransform.output.hll import hll_bases as hll
from lbsntransform.output.hll.base import social, spatial, temporal, topical

from lbsntransform.output.hll.hll_functions import HLLFunctions as HLF

HllBases = Union[
    spatial.LatLngBase, spatial.PlaceBase,
    spatial.CityBase, spatial.CountryBase,
    temporal.DateBase, temporal.MonthBase,
    temporal.YearBase, temporal.MonthLatLngBase,
    temporal.MonthHashtagBase, topical.TermBase,
    topical.EmojiBase, topical.TermLatLngBase,
    topical.HashtagLatLngBase, topical.EmojiLatLngBase,
    social.CommunityBase]


class ProtoHLLMapping():
    """ Methods to map ProtoBuf structure to PG HLL SQL structure."""

    def __init__(self, include_lbsn_bases: List[str] = None):
        if include_lbsn_bases is None:
            include_lbsn_bases = []
        self.include_lbsn_bases = include_lbsn_bases

    @staticmethod
    def update_hll_dicts(
            batched_hll_bases: Dict[Tuple[str, str], Dict[str, HllBases]],
            hll_base_metrics: List[HllBases]):
        """Update batched hll bases with new list of bases, merged metrics

        batched_hll_bases:
            Dict[(facet, base)]: dict(key=str, HllBaseMetrics),
        e.g. batched_hll_bases[('spatial', 'latlng')]:
            dict[
                '71:25': user_hll, post, hll ..
                '5:16': user_hll, post, hll ..
                ]
        """
        for hll_base_metric in hll_base_metrics:
            if hll_base_metric is None:
                continue
            base_dict = batched_hll_bases.get(hll_base_metric.NAME)
            if base_dict is None:
                # skip bases not registered
                continue
            # metric_key = hll_base_metric.get_key_value()
            # metric_key is always a tuple
            # with the unique key (e.g. "(2019-09-01,)")
            # base_dict[metric_key] |= hll_base_metric
            metric_key = hll_base_metric.get_key_value()
            if metric_key not in base_dict:
                base_dict[metric_key] = hll_base_metric
            else:
                base_dict[metric_key] |= hll_base_metric

    def extract_hll_base_metrics(self, record, record_type) -> Optional[
            List[HllBases]]:
        """Combine bases and metrics from Proto LBSN record"""
        record_hll_metrics = self.get_hll_metrics(record)
        if record_hll_metrics is None:
            return
        hll_bases = self.extract_hll_bases(
            record, record_type, self.include_lbsn_bases)
        # turn generator into list
        hll_base_metrics = list(ProtoHLLMapping.update_bases_metrics(
            bases=hll_bases, metrics=record_hll_metrics))
        return hll_base_metrics

    @staticmethod
    def update_bases_metrics(
            bases: List[HllBases],
            metrics: hll.HllMetrics) -> Iterator[HllBases]:
        """Adds/updates metrics to hll_bases"""
        # iterate Namedtuple field names and values
        for key, value in zip(metrics._fields, metrics):
            # key = 'utl_hll', 'upl_hll'
            # value = set/str
            if value is None:
                continue
            for base in bases:
                if key in base.metrics:
                    if key in ('upt_hll', 'utl_hll'):
                        # use update on set
                        base.metrics[key] |= value
                    else:
                        # otherwise add single item
                        base.metrics[key].add(value)
                # return updated base as iterator
                yield base

    def extract_hll_bases(
            self, record, record_type,
            include_lbsn_bases: List[str]) -> List[HllBases]:
        """Extract hll bases from Proto LBSN record

        Depending on LBSNType, multiple bases can be extracted
        e.g.:
        lbsn.Post -> hll.LatLngBase
        lbsn.Post -> hll.PlaceBase
        lbsn.Post -> hll.CityBase
        lbsn.Post -> hll.CountryBase
        lbsn.Post -> hll.DateBase
        lbsn.Post -> hll.MonthBase
        lbsn.Post -> hll.YearBase
        lbsn.Post -> hll.TermBase (multiple)
        bsn.Post -> hll.HashtagBase (multiple)
        (lbsn.Place -> hll.PlaceBase)
        (lbsn.City -> hll.CityBase)
        """
        base_list = []
        # Posts
        if record_type == lbsn.Post.DESCRIPTOR.name:
            # Spatial Facet
            # base from record.post_geoaccuracy
            # see protobuf spec for enum values:
            # UNKNOWN = 0; LATLNG = 1; PLACE = 2; CITY = 3; COUNTRY = 4;
            spatial_base = lbsn.Post.PostGeoaccuracy.Name(
                record.post_geoaccuracy).lower()
            if include_lbsn_bases and spatial_base in include_lbsn_bases:
                base_records = self.make_base(
                    facet='spatial',
                    base=spatial_base,
                    record=record)
                if base_records:
                    base_list.extend(base_records)
            # Temporal Facet
            temporal_bases = [
                'date', 'month', 'year', '_month_latlng', '_month_hashtag']
            temporal_bases = self.filter_bases(
                temporal_bases, include_lbsn_bases)
            base_records = self.make_bases(
                facet='temporal',
                bases=temporal_bases,
                record=record)
            if base_records:
                base_list.extend(base_records)
            # Topical Facet
            topical_bases = [
                'hashtag', 'emoji', 'term', '_term_latlng', '_emoji_latlng',
                '_hashtag_latlng']
            topical_bases = self.filter_bases(
                topical_bases, include_lbsn_bases)
            base_records = self.make_bases(
                facet='topical',
                bases=topical_bases,
                record=record)
            if base_records:
                base_list.extend(base_records)
            social_bases = ['community']
            social_bases = self.filter_bases(
                social_bases, include_lbsn_bases)
            base_records = self.make_bases(
                facet='social',
                bases=social_bases,
                record=record)
            if base_records:
                base_list.extend(base_records)

        # Places
        if record_type == lbsn.Place.DESCRIPTOR.name:
            if include_lbsn_bases and 'place' in include_lbsn_bases:
                base_records = self.make_base(
                    facet='spatial',
                    base='place',
                    record=record)
                if base_records:
                    base_list.extend(base_records)
        if record_type == lbsn.City.DESCRIPTOR.name:
            if include_lbsn_bases and 'city' in include_lbsn_bases:
                base_records = self.make_base(
                    facet='spatial',
                    base='city',
                    record=record)
                if base_records:
                    base_list.extend(base_records)
        if record_type == lbsn.Country.DESCRIPTOR.name:
            if include_lbsn_bases and 'country' in include_lbsn_bases:
                base_records = self.make_base(
                    facet='spatial',
                    base='country',
                    record=record)
                if base_records:
                    base_list.extend(base_records)
        return base_list

    @classmethod
    def filter_bases(
            cls, base_list: List[str],
            include_lbsn_bases: List[str]):
        """Remove bases based on user supplied include list"""
        if not include_lbsn_bases:
            # if empty
            return base_list
        base_list_filtered = []
        for base in base_list:
            if base in include_lbsn_bases:
                base_list_filtered.append(base)
        return base_list_filtered

    @classmethod
    def make_bases(cls, facet: str, bases: List[str], record):
        """Create list of hllBases list of bases and a single lbsnRecord"""
        base_list = []
        for base in bases:
            base_records = cls.make_base(
                facet=facet,
                base=base,
                record=record)
            if base_records:
                base_list.extend(base_records)
        return base_list

    @classmethod
    def make_base(cls, facet: str, base: str, record):
        """Create list of hllBases from a single lbsnRecord"""
        base_records = hll.base_factory(
            facet=facet,
            base=base,
            record=record)
        return base_records

    @classmethod
    def get_hll_metrics(cls, record) -> hll.HllMetrics:
        """Extracts hll metrics based on record type"""
        dict_switcher = {
            lbsn.Origin().DESCRIPTOR.name: cls.get_origin_metrics,
            lbsn.Country().DESCRIPTOR.name: cls.get_country_metrics,
            lbsn.City().DESCRIPTOR.name: cls.get_city_metrics,
            lbsn.Place().DESCRIPTOR.name: cls.get_place_metrics,
            lbsn.User().DESCRIPTOR.name: cls.get_user_metrics,
            lbsn.UserGroup().DESCRIPTOR.name: cls.get_usergroup_metrics,
            lbsn.Post().DESCRIPTOR.name: cls.get_post_metrics,
            lbsn.PostReaction().DESCRIPTOR.name: cls.get_postreaction_metrics,
            lbsn.Relationship().DESCRIPTOR.name: cls.get_relationship_metrics
        }
        extract_function = dict_switcher.get(record.DESCRIPTOR.name)
        record_hll_metrics = extract_function(record)
        return record_hll_metrics

    @staticmethod
    def get_origin_metrics(record) -> hll.HllMetrics:
        """Get hll metrics from lbsn.Origin record"""
        return

    @staticmethod
    def get_country_metrics(record) -> hll.HllMetrics:
        """Get hll metrics from lbsn.Country record"""
        return

    @staticmethod
    def get_city_metrics(record) -> hll.HllMetrics:
        """Get hll metrics from lbsn.City record"""
        return

    @staticmethod
    def get_place_metrics(record) -> hll.HllMetrics:
        """Get hll metrics from lbsn.Place record"""
        place_hll = HLF.hll_concat_origin_guid(record)
        hll_metrics = hll.HllMetrics(place_hll=place_hll)
        return hll_metrics

    @staticmethod
    def get_user_metrics(record) -> hll.HllMetrics:
        """Get hll metrics from lbsn.User record"""
        return

    @staticmethod
    def get_usergroup_metrics(record) -> hll.HllMetrics:
        """Get hll metrics from lbsn.UserGroup record"""
        return

    @staticmethod
    def get_post_metrics(record) -> hll.HllMetrics:
        """Get hll metrics from lbsn.Post record"""
        post_hll = HLF.hll_concat_origin_guid(record)
        user_hll = HLF.hll_concat_user(record)
        date_hll = HLF.hll_concat_userday(record)
        latlng_hll = HLF.hll_concat_latlng(record)
        place_hll = HLF.hll_concat_place(record)
        upt_hll = HLF.hll_concat_upt_hll(record)
        hll_metrics = hll.HllMetrics(
            post_hll=post_hll, user_hll=user_hll,
            date_hll=date_hll, latlng_hll=latlng_hll,
            upt_hll=upt_hll, place_hll=place_hll)
        return hll_metrics

    @staticmethod
    def get_postreaction_metrics(record) -> hll.HllMetrics:
        """Get hll metrics from lbsn.PostReaction record"""
        return

    @staticmethod
    def get_relationship_metrics(record) -> hll.HllMetrics:
        """Get hll metrics from lbsn.Relationship record"""
        return
