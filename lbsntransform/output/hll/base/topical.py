# -*- coding: utf-8 -*-

"""Hll bases for topical facet
"""

from typing import Tuple, Union

from lbsnstructure import lbsnstructure_pb2 as lbsn
from lbsntransform.output.hll import hll_bases as hll
from lbsntransform.tools.helper_functions import HelperFunctions as HF

FACET = 'topical'


class TopicalBase(hll.HllBase):
    """Intermediate topical base class that extends HllBase
    for HashtagBase, EmojiBase and TermBase
    """

    def __init__(self):
        super().__init__()
        self.metrics['latlng_hll'] = set()
        self.metrics['place_hll'] = set()
        self.metrics['pud_hll'] = set()


class HashtagBase(TopicalBase):
    """Extends Topical Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='hashtag')

    def __init__(self, hashtag: str = None):
        super().__init__()
        self.key['hashtag'] = None
        if hashtag is None:
            # init empty
            return
        self.key['hashtag'] = hashtag.lower()


class EmojiBase(TopicalBase):
    """Extends Topical Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='emoji')

    def __init__(self, emoji: str = None):
        super().__init__()
        self.key['emoji'] = None
        if emoji is None:
            # init empty
            return
        self.key['emoji'] = emoji


class TermBase(TopicalBase):
    """Extends Topical Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='term')

    def __init__(self, term: str = None):
        super().__init__()
        self.key['term'] = None
        if term is None:
            # init empty
            return
        self.key['term'] = term.lower()


class TopicBase(TopicalBase):
    """Extends Topical Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='topic')

    def __init__(self, topic: Tuple[str] = None):
        super().__init__()
        self.key['topic'] = None
        if topic is None:
            # init empty
            return
        self.key['topic'] = topic


class DomainBase(TopicalBase):
    """Extends Topical Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='domain')

    def __init__(self, domain: str = None):
        super().__init__()
        self.key['domain'] = None
        if domain is None:
            # init empty
            return
        self.key['domain'] = domain


class TemplateBase(TopicalBase):
    """Example Base class that extends TopicalBase

    Additional steps:

    * in shared_structure_proto_hlldb.py: extract_hll_bases(),
        define which lbsn.records are mapped to this class
    * if multiple TemplateBase can be extracted from a single lbsn record
        (e.g. such as multiple HashtagBase for a single lbsn.Post),
        update process in hll_bases.py: base_factory()
    * in submit_data.py, add TemplateBase to batched_hll_records so
        they are actually used in the mapping procedure
    * if you need specific metrics/measurements that are noit yet defined,
        update HllMetrics and get_hll_metrics()
        in shared_structure_proto_hlldb.py
    """
    # define the name reference (str-identifier) for this class
    # any class with NAME is automatically registered
    NAME = hll.HllBaseRef(facet=FACET, base='topicexample')

    def __init__(self, record: Union[
            lbsn.Post,
            lbsn.Place] = None):
        """Initialize TemplateBase from lbsn record

        Define here from which lbsn record types
        this base can be initialized, example: lbsn.Post, lbsn.Place
        """
        # initialize parent class (TopicalBase)
        super().__init__()

        # TemplateBase can also be initialized empty,
        # for this reason we specify the structure
        # before mapping record values
        self.key['topic_base_id'] = None
        self.attrs['topic_attr1'] = None
        self.attrs['topic_attr2'] = None
        self.attrs['topic_attr3'] = None
        # TemplateBase inherits from TopicalBase
        # thus, metrics latlng_hll, place_hll and pud_hll
        # are already defined. Specify additional metrics below
        # or remove inheritance and define from scratch
        self.metrics['utl_hll'] = set()
        # if no record is supplied, init empty
        if record is None:
            return
        # now it's time to extract (map) lbsn record to this base:
        # * first define how the key is extracted
        self.key['topic_base_id'] = self.extract_topic_base_id(record)
        # * afterwards define how additional (optional) attributes are
        #    extracted
        self.key['topic_attr1'] = self.extract_topic_base_attrs(record)

    @classmethod
    def extract_topic_base_id(cls, record: Union[lbsn.Post, lbsn.Place]):
        """Template method: define how base key is extracted from record"""
        return

    @classmethod
    def extract_topic_base_attrs(cls, record: Union[lbsn.Post, lbsn.Place]):
        """Template method: define how additional attrs are
        extracted from record
        """
        return


class TermLatLngBase(hll.HllBase):
    """Composite Base (c-base) that extends from HLL base Class

    Note: To distinguish c-bases which are composite bases combining
    aspects from multiple facets, they're termed with a leading underscore
    """
    NAME = hll.HllBaseRef(facet=FACET, base='_term_latlng')

    def __init__(self, record: lbsn.Post = None, term: str = None):
        super().__init__()
        self.key['latitude'] = None
        self.key['longitude'] = None
        self.key['term'] = None
        self.attrs['latlng_geom'] = None
        self.metrics['pud_hll'] = set()
        if term is None:
            # init empty
            return
        self.key['term'] = term.lower()
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


class HashtagLatLngBase(hll.HllBase):
    """Composite Base (c-base) that extends from HLL base Class

    Note: To distinguish c-bases which are composite bases combining
    aspects from multiple facets, they're termed with a leading underscore
    """
    NAME = hll.HllBaseRef(facet=FACET, base='_hashtag_latlng')

    def __init__(self, record: lbsn.Post = None, hashtag: str = None):
        super().__init__()
        self.key['latitude'] = None
        self.key['longitude'] = None
        self.key['hashtag'] = None
        self.attrs['latlng_geom'] = None
        self.metrics['pud_hll'] = set()
        if hashtag is None:
            # init empty
            return
        self.key['hashtag'] = hashtag.lower()
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


class EmojiLatLngBase(hll.HllBase):
    """Composite Base (c-base) that extends from HLL base Class

    Note: To distinguish c-bases which are composite bases combining
    aspects from multiple facets, they're termed with a leading underscore
    """
    NAME = hll.HllBaseRef(facet=FACET, base='_emoji_latlng')

    def __init__(self, record: lbsn.Post = None, emoji: str = None):
        super().__init__()
        self.key['latitude'] = None
        self.key['longitude'] = None
        self.key['emoji'] = None
        self.attrs['latlng_geom'] = None
        self.metrics['pud_hll'] = set()
        if emoji is None:
            # init empty
            return
        self.key['emoji'] = emoji
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
