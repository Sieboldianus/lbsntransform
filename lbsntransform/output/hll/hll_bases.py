# -*- coding: utf-8 -*-

"""
Sample bases and metrics for HLL aggregation


The base classes shown here are only examples that illustrate how to extract
typical bases and metrics from Location Based Social Media (LBSN). The
structure is motivated by the 4 facets of Social Media discussed in [1].
Base classes are organized per facet in subfolders base/facet

A template-class is provided that allows extending this module for individual
needs (see class topical.TemplateBase). The general idea is that each class has

* a NAME, which is a reference of type Tuple(str, str) consisting of (1)
    its facet (either spatial, temporal, topical or social) and (2) a
    unique base reference (e.g. latlng, place, region, city or country). In
    our examples, base classes per facet follow the granularity hierarchy
    proposed in [4]
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

[4] Löchner, M., Dunkel, A., & Burghardt, D. (2018).
A privacy-aware model to process data from location-based social media.
"""

import inspect
import sys
from collections import OrderedDict, namedtuple
from typing import List

from lbsnstructure import lbsnstructure_pb2 as lbsn
from lbsntransform.tools.helper_functions import HelperFunctions as HF

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
    """Function to dynamically register base classes for each facet"""
    for facet in ["social", "spatial", "topical", "temporal"]:
        for __, obj in inspect.getmembers(
                sys.modules[f"lbsntransform.output.hll.base.{facet}"]):
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

    Any bases that require special hooks need to be registered here. This
    applies, for example, for bases that can appear multiple times
    in a single record (hashtags, emoji, terms etc.).
    """
    records = []
    base_structure = BASE_REGISTER.get((facet, base))
    if base_structure is None:
        return
    # for topical bases (e.g. hashtag, emoji, term)
    # multiple bases can be created
    # from a single lbsn record
    if base == 'hashtag':
        # only explicit hashtags
        tag_terms = HF.filter_terms(record.hashtags)
        for tag in tag_terms:
            records.append(
                base_structure(tag))
    elif base == 'emoji':
        # do nothing
        all_post_emoji = HF.get_all_post_emoji(record.post_body)
        for emoji in all_post_emoji:
            # create base for each term
            records.append(
                base_structure(emoji))
    elif base == 'term':
        # any term mentioned in title,
        # body or hashtag
        all_post_terms = HF.get_all_post_terms(record)
        for term in all_post_terms:
            # create base for each term
            records.append(
                base_structure(term))
    elif base == 'topic':
        raise NotImplementedError(
            "Parsing of Topics base is currently not implemented")
    elif base == 'domain':
        raise NotImplementedError(
            "Parsing of Domains base is currently not implemented")
    elif base == '_term_latlng':
        # any term mentioned in title,
        # body or hashtag
        all_post_terms = HF.get_all_post_terms(record)
        for term in all_post_terms:
            # create base for each term
            records.append(
                base_structure(record=record, term=term))
    elif base == '_hashtag_latlng':
        # any hashtag explicitly used
        tag_terms = HF.filter_terms(record.hashtags)
        for tag in tag_terms:
            records.append(
                base_structure(record=record, hashtag=tag))
    elif base == '_emoji_latlng':
        # any term mentioned in title,
        # body or hashtag
        all_post_emoji = HF.get_all_post_emoji(record.post_body)
        for emoji in all_post_emoji:
            # create base for each term
            records.append(
                base_structure(record=record, emoji=emoji))
    elif base == '_month_hashtag':
        # any hashtag explicitly used
        tag_terms = HF.filter_terms(record.hashtags)
        for tag in tag_terms:
            records.append(
                base_structure(record=record, hashtag=tag))
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
        return list(self.key.keys())

    def get_attr_keys(self):
        """Returns attr keys for base
        """
        return list(self.attrs.keys())

    def get_metric_keys(self):
        """Returns metric keys for base
        """
        return list(self.metrics.keys())

    def get_sql_header(self) -> List[str]:
        """Get joined header for hll upsert sql
        Concat column names for key, attrs and metrics, e.g.:
        latitude, longitude, latlng_geom, user_hll, post_hll, date_hll, utl_hll
        """
        base_key_cols = [self.key.keys()]
        base_attr_cols = [self.attrs.keys()]
        base_metrics_cols = [self.metrics.keys()]
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
