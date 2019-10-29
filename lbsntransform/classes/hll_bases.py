# -*- coding: utf-8 -*-

"""
Sample bases and metrics for HLL aggregation


The base classes shown here are only examples that illustrate how to extract
typical bases and metrics from Location Based Social Media (LBSN). The
structure is motivated by the 4 facets of Social Media discussed in [1].

A template-class is provided that allows extending this module for individual
needs (see class BaseTemplate). The general idea is that each class has

* a NAME, which is a reference of type Tuple(str, str) consisting of (1)
    its facet (either spatial, temporal, topical or social) and its
    specific base reference (e.g. latlng, place, region, city or country)
* a Key, which is a unique reference (i.e. the "base") that is measured
* a list of addititional (optional) attributes for the base, e.g. the lat-lng
    key as Postgis Geometry, or a name for the place etc.
* a list of (hll) metrics that are measured for the base (the "overlay"), e.g.
    a list of post_guids ("post_hll"), or user_guids ("user_hll"), or more
    complex metrics such as date_hll (user days, as termed by [2]). These
    lists will be transformed into a "hll shard".

Additional Notes:
* the structure here is closely aligned with the SQL hll files
    maintained in [3], if you add any classes or metrics, make youre they're
    also updated in your hll db
* order is important: the sql commands are constructed dynamically from the
    class structures defined here, thus it is important that order of keys,
    attrs and metrics exactly match the sql db definitions. For this reason,
    OrderedDicts() are used, which store the order in which keys are added
* most classes here make use of (multiple) class inheritance to reduce code
    duplication
* how bases and metrics are mapped from lbsnstructure entirely depends on
    individual needs, the mappings demonstrated here are mere examples. Any
    complex mapping can be added to any of the classes and from any of the
    lbsnstructure objects (e.g. lbsn.Post, lbsn.Place, lbsn.Reaction,
    lbsn.User etc.)

[1] Dunkel, A., Andrienko, G., Andrienko, N., Burghardt, D., Hauthal,
E., & Purves, R. (2019). A conceptual framework for studying collective
reactions to events in location-based social media. International
Journal of Geographical Information Science, 33, 4, 780-804.
[2] Sessions, C., Wood, S. A., Rabotyagov, S., & Fisher, D. M. (2016).
Measuring recreational visitation at U.S. National Parks with
crowd-sourced photo-graphs. Journal of Environmental Management,
183, 703–711. DOI: 10.1016/j.jenvman.2016.09.018
[3] https://gitlab.vgiscience.de/lbsn/databases/hlldb
"""

import sys
import inspect
from collections import namedtuple, OrderedDict
from typing import Tuple, List, Any, Dict, Union

from lbsnstructure import lbsnstructure_pb2 as lbsn

from .helper_functions import HelperFunctions as HF
from .hll_functions import HLLFunctions as HLF

# named tuple of defined hll metrics
HllMetrics = namedtuple(  # pylint: disable=C0103
    'HllMetricsTuple',
    'user_hll post_hll date_hll latlng_hll upl_hll utl_hll '
    'upt_hll term_hll place_hll', defaults=(None,) * 9)

HllBaseRef = namedtuple('HllBaseRefTuple', 'facet base')
BaseRecordValue = namedtuple('BaseRecordValue', 'record metrics')

# global static variable (dict) to register
# the base classes defined in this module, e.g.
# BASE_REGISTER = {
#     LatLngBase.NAME: LatLngBase,
#     PlaceBase.NAME: PlaceBase,
#     CityBase.NAME: CityBase,
#     ...
# }
BASE_REGISTER = {}

# global static dict for (hard-coded) base header,
# list of sql column names in correct order
# BASE_HEADER = {}
BASE_KEY = {}
BASE_ATTRS = {}
BASE_METRICS = {}


def register_classes():
    """Function to dynamically register base classes in this module"""
    for __, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            if hasattr(obj, 'NAME'):
                BASE_REGISTER[obj.NAME] = obj
                BASE_KEY[obj.NAME] = obj().get_key()
                BASE_ATTRS[obj.NAME] = obj().get_attr_keys()
                BASE_METRICS[obj.NAME] = obj().get_metric_keys()


def merge_base_metrics(base1, base2):
    """Merge two base-metrics by union of its set values"""
    # merge metric dicts
    for key in base1.metrics.keys():
        new_set = base2.metrics.get(key)
        if new_set is None:
            continue
        base1.metrics[key] |= new_set


def base_factory(facet=None, base=None, record: lbsn.Post = None):
    """Base is initialized based on facet-base tuple
    and constructed by parsing lbsn records
    """
    records = []
    base_structure = BASE_REGISTER.get((facet, base))
    if base_structure is None:
        return
    # for topical bases (e.g. hashtag, emoji, term)
    # multiple bases can be created
    # from a single lbsn record
    if base == 'hashtag':
        tag_terms = set(record.hashtags)
        for tag in tag_terms:
            records.append(
                base_structure(tag))
    elif base == 'emoji':
        # do nothing
        pass
    elif base == 'term':
        body_terms = HF.select_terms(
            record.post_body)
        title_terms = HF.select_terms(
            record.post_title)
        tag_terms = {tag for tag in record.hashtags if len(tag) > 2}
        all_post_terms = set.union(
            body_terms, title_terms, tag_terms)
        for term in all_post_terms:
            records.append(
                base_structure(term))
    elif base == 'topic':
        pass
    elif base == 'domain':
        pass
    else:
        # init for all other bases with single lbsn record
        record = base_structure(record)
        records.append(record)
    return records


class HllBase():
    """Shared attributes for all hll bases"""

    def __init__(self):
        # the key, used as primary (unique) key
        # in the relational db, e.g. 2019-01-01
        # keys can consist of multiple parts, e.g.
        # (lat, lng) which then form composite
        # primary keys in the db
        self.key = OrderedDict()
        # any additional attributes that
        # are stored additionally to the
        # key, e.g. for date-key
        # name: "New Year's Day"
        self.attrs = OrderedDict()
        # the hll-metrics, in constistent
        # order matching the SQL upsert order
        self.metrics = OrderedDict([
            ('user_hll', set()),
            ('post_hll', set())
        ])

    def __ior__(self, other):
        """Implements bitwise or using the | operator.
        """
        if other is None:
            return self
        merge_base_metrics(self, other)
        return self

    def __repr__(self):
        """Implement custom format str for debug"""
        return HF.format_base_repr(self)

    def get_key_value(self):
        """Returns key value for base
        """
        return tuple(self.key.values())

    def get_key(self):
        """Returns key name for base
        """
        return [key for key in self.key.keys()]

    def get_attr_keys(self):
        """Returns attr keys for base
        """
        return [key for key in self.attrs.keys()]

    def get_metric_keys(self):
        """Returns metric keys for base
        """
        return [key for key in self.metrics.keys()]

    def get_sql_header(self) -> str:
        """Get joined header for hll upsert sql
        Concat column names for key, attrs and metrics, e.g.:
        latitude, longitude, latlng_geom, user_hll, post_hll, date_hll, utl_hll
        """
        base_key_cols = [key for key in self.key.keys()]
        base_attr_cols = [key for key in self.attrs.keys()]
        base_metrics_cols = [key for key in self.metrics.keys()]
        return base_key_cols + base_attr_cols + base_metrics_cols

    def get_prepared_record(self):
        """Return prepared sql values tuple

        Consisting of
        * key and attributes tuple (base_record) = the record
        * metric dicts with values = the metrics
        """
        base_record = tuple(self.key.values())
        for attr in self.attrs.values():
            base_record += (attr,)
        return BaseRecordValue(base_record, self.metrics)


class LatLngBase(HllBase):
    """Extends Base Class"""
    # base reference, eg.
    # e.g.: facet: temporal, base: date
    NAME = HllBaseRef(facet='spatial', base='latlng')

    def __init__(self, record: lbsn.Post = None):
        super().__init__()
        # init key and any additional attributes
        self.key['latitude'] = None
        self.key['longitude'] = None
        self.attrs['latlng_geom'] = None
        # init additional metrics
        # beyond those defined inHllBase
        self.metrics['date_hll'] = set()
        self.metrics['utl_hll'] = set()
        if record is None:
            # init empty
            return
        if isinstance(record, lbsn.Post):
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
                "Parsing of LatLngBase only supported "
                "from lbsn.Post")


class PlaceBase(HllBase):
    """Extends HllBase Class"""
    NAME = HllBaseRef(facet=LatLngBase.NAME.facet, base='place')

    def __init__(self, record: Union[
            lbsn.Post,
            lbsn.Place] = None):
        super().__init__()
        self.key['place_guid'] = None
        self.attrs['geom_center'] = None
        self.attrs['geom_area'] = None
        self.attrs['name'] = None
        self.metrics['date_hll'] = set()
        self.metrics['utl_hll'] = set()
        if record is None:
            return
        if isinstance(record, lbsn.Post):
            # Post can be of Geoaccuracy "Place" without any
            # actual place id assigned (e.g. Flickr Geoaccuracy level < 10)
            # in this case, concat lat:lng as primary key
            coordinates_geom = record.post_latlng
            if not record.place_pkey.id:
                coordinates = HF.get_coordinates_from_ewkt(
                    coordinates_geom
                )
                self.key['place_guid'] = HLF.hll_concat(
                    [coordinates.lat, coordinates.lng])
            else:
                self.key['place_guid'] = record.place_pkey.id
            # additional (optional) attributes
            # formatted ready for sql upsert
            self.attrs['geom_center'] = HF.return_ewkb_from_geotext(
                coordinates_geom)
            # geom_area not available from lbsn.Post
        elif isinstance(record, lbsn.Place):
            coordinates_geom = record.geom_center
            coordinates = HF.get_coordinates_from_ewkt(
                coordinates_geom
            )
            self.key['place_guid'] = record.place_pkey.id
            # self.key['place_guid'] = HLF.hll_concat(
            #     [coordinates.lat, coordinates.lng])
            self.attrs['geom_center'] = HF.return_ewkb_from_geotext(
                coordinates_geom)
            self.attrs['geom_area'] = HF.return_ewkb_from_geotext(
                record.geom_area)
            self.attrs['name'] = record.name


class SpatialBase(HllBase):
    """Intermediate spatial base class that extends HllBase
    for Place, City, Region and Country
    sharing common attributes
    """
    FACET = 'spatial'

    def __init__(self, record: Union[
            lbsn.Post,
            lbsn.Place,
            lbsn.City,
            lbsn.Country] = None):
        super().__init__()
        self.key["guid"] = None
        self.attrs['name'] = None
        self.attrs['geom_center'] = None
        self.attrs['geom_area'] = None
        self.metrics['date_hll'] = set()
        self.metrics['utl_hll'] = set()
        self.metrics['latlng_hll'] = set()
        if record is None:
            # init empty
            return
        name = None
        geom_area = None
        if isinstance(record, lbsn.Post):
            coordinates_geom = record.post_latlng
            coordinates = HF.get_coordinates_from_ewkt(
                coordinates_geom
            )
            # use concat lat:lng as key of no place_key available
            # this should later implement assignemnt based on area
            # intersection
            self.key["guid"] = HLF.hll_concat(
                [coordinates.lat, coordinates.lng])
        elif isinstance(record, (lbsn.Place, lbsn.City, lbsn.Country)):
            name = HF.null_check(record.name)
            coordinates_geom = record.geom_center
            geom_area = record.geom_area
            # use key from place, city or country record
            self.key["guid"] = HLF.hll_concat_origin_guid(record)

        self.attrs['name'] = name
        self.attrs['geom_center'] = HF.return_ewkb_from_geotext(
            coordinates_geom)
        self.attrs['geom_area'] = HF.return_ewkb_from_geotext(
            geom_area)


class CityBase(SpatialBase):
    """Extends Spatial Base Class"""
    NAME = HllBaseRef(facet=SpatialBase.FACET, base='city')

    def __init__(self, record: lbsn.Post = None):
        super().__init__(record)
        # rename key accordingly
        self.key["city_guid"] = self.key.pop("guid")


class RegionBase(SpatialBase):
    """Extends Spatial Base Class"""
    NAME = HllBaseRef(facet=SpatialBase.FACET, base='region')

    def __init__(self, record: lbsn.Post = None):
        super().__init__(record)
        # rename key accordingly
        self.key["region_guid"] = self.key.pop("guid")


class CountryBase(SpatialBase):
    """Extends Spatial Base Class"""
    NAME = HllBaseRef(facet=SpatialBase.FACET, base='country')

    def __init__(self, record: lbsn.Post = None):
        super().__init__(record)
        # rename key accordingly
        self.key["country_guid"] = self.key.pop("guid")


class TemporalBase(HllBase):
    """Intermediate temporal base class that extends HllBase
    for a number of temporal classes
    """
    FACET = 'temporal'

    def __init__(self):
        super().__init__()


class TimestampBase(TemporalBase):
    """Extends Base Class"""
    NAME = HllBaseRef(facet=TemporalBase.FACET, base='timestamp')

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
    NAME = HllBaseRef(facet=TemporalBase.FACET, base='date')

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
    NAME = HllBaseRef(facet=TemporalBase.FACET, base='month')

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
    NAME = HllBaseRef(facet=TemporalBase.FACET, base='year')

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
    NAME = HllBaseRef(facet=TemporalBase.FACET, base='timeofday')

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
    NAME = HllBaseRef(facet=TemporalBase.FACET, base='hourofday')

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
    NAME = HllBaseRef(facet=TemporalBase.FACET, base='dayofweek')

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
    NAME = HllBaseRef(facet=TemporalBase.FACET, base='dayofmonth')

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
    NAME = HllBaseRef(facet=TemporalBase.FACET, base='dayofyear')

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
    NAME = HllBaseRef(facet=TemporalBase.FACET, base='monthofyear')

    def __init__(self, record: lbsn.Post = None):
        super().__init__()
        self.key['monthofyear'] = None
        if record is None:
            # init empty
            return
        post_date_time = HLF.merge_dates_post(
            record)
        self.key['monthofyear'] = post_date_time.month


class TopicalBase(HllBase):
    """Intermediate topical base class that extends HllBase
    for HashtagBase, EmojiBase and TermBase
    """
    FACET = 'topical'

    def __init__(self):
        super().__init__()
        self.metrics['latlng_hll'] = set()
        self.metrics['place_hll'] = set()
        self.metrics['date_hll'] = set()


class HashtagBase(TopicalBase):
    """Extends Topical Base Class"""
    NAME = HllBaseRef(facet=TopicalBase.FACET, base='hashtag')

    def __init__(self, hashtag: str = None):
        super().__init__()
        self.key['hashtag'] = None
        if hashtag is None:
            # init empty
            return
        self.key['hashtag'] = hashtag.lower()


class EmojiBase(TopicalBase):
    """Extends Topical Base Class"""
    NAME = HllBaseRef(facet=TopicalBase.FACET, base='emoji')

    def __init__(self, emoji: str = None):
        super().__init__()
        self.key['emoji'] = None
        if emoji is None:
            # init empty
            return
        self.key['emoji'] = emoji


class TermBase(TopicalBase):
    """Extends Topical Base Class"""
    NAME = HllBaseRef(facet=TopicalBase.FACET, base='term')

    def __init__(self, term: str = None):
        super().__init__()
        self.key['term'] = None
        if term is None:
            # init empty
            return
        self.key['term'] = term.lower()


class TopicBase(TopicalBase):
    """Extends Topical Base Class"""
    NAME = HllBaseRef(facet=TopicalBase.FACET, base='topic')

    def __init__(self, topic: Tuple[str] = None):
        super().__init__()
        self.key['topic'] = None
        if topic is None:
            # init empty
            return
        self.key['topic'] = topic


class DomainBase(TopicalBase):
    """Extends Topical Base Class"""
    NAME = HllBaseRef(facet=TopicalBase.FACET, base='domain')

    def __init__(self, domain: str = None):
        super().__init__()
        self.key['domain'] = None
        if domain is None:
            # init empty
            return
        self.key['domain'] = domain


class SocialBase(HllBase):
    """Intermediate social base class that extends HllBase
    for common social base attributes
    """
    FACET = 'social'

    def __init__(self):
        super().__init__()
        self.metrics['latlng_hll'] = set()
        self.metrics['place_hll'] = set()
        self.metrics['date_hll'] = set()


class UserBase(SocialBase):
    """Extends Social Base Class"""
    NAME = HllBaseRef(facet=SocialBase.FACET, base='user')

    def __init__(self, record: lbsn.User = None):
        super().__init__()
        self.key['user_guid'] = None
        if record is None:
            # init empty
            return
        # TODO: implement one-way-hashing
        self.key['user_guid'] = HLF.hll_concat_origin_guid(record)


class FriendsBase(SocialBase):
    """Extends Social Base Class"""
    NAME = HllBaseRef(facet=SocialBase.FACET, base='friends')

    def __init__(self, friends_record: Tuple[lbsn.User, lbsn.User] = None):
        super().__init__()
        self.key['user_guid'] = None
        self.key['user_guid_friend'] = None
        if friends_record is None:
            # init empty
            return
        # TODO: implement one-way-hashing
        self.key['user_guid'] = HLF.hll_concat_origin_guid(
            friends_record[0])
        self.key['user_guid_friend'] = HLF.hll_concat_origin_guid(
            friends_record[1])


class CommunityBase(SocialBase):
    """Extends Social Base Class"""
    NAME = HllBaseRef(facet=SocialBase.FACET, base='community')

    def __init__(self, record: lbsn.Origin = None):
        super().__init__()
        self.attrs['name'] = None
        self.key['id'] = None
        if record is None:
            # init empty
            return
        self.attrs['name'] = record.DESCRIPTOR.name
        self.key['id'] = record.origin_id


class CultureBase(SocialBase):
    """Extends Social Base Class"""
    NAME = HllBaseRef(facet=SocialBase.FACET, base='culture')

    def __init__(self, record: lbsn.Language = None):
        super().__init__()
        self.key['id'] = None
        if record is None:
            # init empty
            return
        self.key['id'] = record.language_short
