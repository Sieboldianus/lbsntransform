# -*- coding: utf-8 -*-

"""Hll bases for temporal facet
"""

from lbsnstructure import lbsnstructure_pb2 as lbsn
from lbsntransform.output.hll import hll_bases as hll

from lbsntransform.output.hll.hll_functions import HLLFunctions as HLF
from lbsntransform.tools.helper_functions import HelperFunctions as HF

FACET = 'temporal'


class TemporalBase(hll.HllBase):
    """Intermediate temporal base class that extends HllBase
    for a number of temporal classes
    """

    def __init__(self):
        super().__init__()


class TimestampBase(TemporalBase):
    """Extends Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='timestamp')

    def __init__(self, record: lbsn.Post = None):
        super().__init__()
        self.key["timestamp"] = None
        if record is None:
            # init empty
            return
        post_date_time = HLF.merge_dates_post(
            record)
        self.key["timestamp"] = post_date_time


class DateBase(TemporalBase):
    """Extends Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='date')

    def __init__(self, record: lbsn.Post = None):
        super().__init__()
        self.key['date'] = None
        self.attrs['name'] = None
        if record is None:
            # init empty
            return
        post_date_time = HLF.merge_dates_post(
            record)
        if post_date_time is None:
            return
        # optional: add name of date (e.g. "New Year's Day")
        self.key['date'] = post_date_time.date()


class MonthBase(TemporalBase):
    """Extends Temporal Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='month')

    def __init__(self, record: lbsn.Post = None):
        super().__init__()
        self.key['year'] = None
        self.key['month'] = None
        if record is None:
            # init empty
            return
        post_date_time = HLF.merge_dates_post(
            record)
        if post_date_time is None:
            return
        date = post_date_time.date()
        self.key['year'] = date.year
        self.key['month'] = date.month


class YearBase(TemporalBase):
    """Extends Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='year')

    def __init__(self, record: lbsn.Post = None):
        super().__init__()
        self.key['year'] = None
        if record is None:
            # init empty
            return
        post_date_time = HLF.merge_dates_post(
            record)
        if post_date_time is None:
            return
        date = post_date_time.date()
        self.key['year'] = date.year


class TimeofdayBase(TemporalBase):
    """Extends Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='timeofday')

    def __init__(self, record: lbsn.Post = None):
        super().__init__()
        self.key['timeofday'] = None
        if record is None:
            # init empty
            return
        post_date_time = HLF.merge_dates_post(
            record)
        # remove microseconds from datetime
        self.key['timeofday'] = post_date_time.time.replace(
            microsecond=0)


class HourofdayBase(TemporalBase):
    """Extends Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='hourofday')

    def __init__(self, record: lbsn.Post = None):
        super().__init__()
        self.key['hourofday'] = None
        if record is None:
            # init empty
            return
        post_date_time = HLF.merge_dates_post(
            record)
        # remove seconds and microseconds from datetime
        self.key['hourofday'] = post_date_time.time.replace(
            second=0, microsecond=0)


class DayofweekBase(TemporalBase):
    """Extends Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='dayofweek')

    def __init__(self, record: lbsn.Post = None):
        super().__init__()
        self.key['weekday'] = None
        if record is None:
            # init empty
            return
        post_date_time = HLF.merge_dates_post(
            record)
        self.key['weekday'] = post_date_time.weekday


class DayofmonthBase(TemporalBase):
    """Extends Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='dayofmonth')

    def __init__(self, record: lbsn.Post = None):
        super().__init__()
        self.key['dayofmonth'] = None
        if record is None:
            # init empty
            return
        post_date_time = HLF.merge_dates_post(
            record)
        self.key['dayofmonth'] = post_date_time.day


class DayofyearBase(TemporalBase):
    """Extends Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='dayofyear')

    def __init__(self, record: lbsn.Post = None):
        super().__init__()
        self.key['month'] = None
        self.key['day'] = None
        if record is None:
            # init empty
            return
        post_date_time = HLF.merge_dates_post(
            record)
        self.key['month'] = post_date_time.month
        self.key['day'] = post_date_time.day


class MonthofyearBase(TemporalBase):
    """Extends Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='monthofyear')

    def __init__(self, record: lbsn.Post = None):
        super().__init__()
        self.key['monthofyear'] = None
        if record is None:
            # init empty
            return
        post_date_time = HLF.merge_dates_post(
            record)
        self.key['monthofyear'] = post_date_time.month

class MonthHashtagBase(hll.HllBase):
    """Composite Base (c-base) that extends from HLL base Class

    Note: To distinguish c-bases which are composite bases combining
    aspects from multiple facets, they're termed with a leading underscore
    """
    NAME = hll.HllBaseRef(facet=FACET, base='_month_hashtag')

    def __init__(self, record: lbsn.Post = None, hashtag: str = None):
        super().__init__()
        self.key['year'] = None
        self.key['month'] = None
        self.key['hashtag'] = None
        if hashtag is None:
            # init empty
            return
        self.key['hashtag'] = hashtag.lower()
        if record is None:
            # init empty
            return
        if isinstance(record, lbsn.Post):
            post_date_time = HLF.merge_dates_post(
                record)
            if post_date_time is None:
                return
            date = post_date_time.date()
            self.key['year'] = date.year
            self.key['month'] = date.month
        else:
            raise ValueError(
                "Parsing of MonthHashtagBase only supported "
                "from lbsn.Post")

class MonthLatLngBase(hll.HllBase):
    """Composite Base (c-base) that extends from HLL base Class

    Note: To distinguish c-bases which are composite bases combining
    aspects from multiple facets, they're termed with a leading underscore
    """
    NAME = hll.HllBaseRef(facet=FACET, base='_month_latlng')

    def __init__(self, record: lbsn.Post = None, hashtag: str = None):
        super().__init__()
        self.key['year'] = None
        self.key['month'] = None
        self.key['latitude'] = None
        self.key['longitude'] = None
        self.attrs['latlng_geom'] = None
        if record is None:
            # init empty
            return
        if isinstance(record, lbsn.Post):
            post_date_time = HLF.merge_dates_post(
                record)
            if post_date_time is None:
                return
            date = post_date_time.date()
            self.key['year'] = date.year
            self.key['month'] = date.month

            coordinates_geom = record.post_latlng
            coordinates = HF.get_coordinates_from_ewkt(
                coordinates_geom
            )
            self.key['latitude'] = coordinates.lat
            self.key['longitude'] = coordinates.lng
            # additional (optional) attributes
            # formatted ready for sql upsert
            self.attrs['latlng_geom'] = HF.return_ewkb_from_geotext(
                coordinates_geom)
        else:
            raise ValueError(
                "Parsing of MonthLatLngBase only supported "
                "from lbsn.Post")