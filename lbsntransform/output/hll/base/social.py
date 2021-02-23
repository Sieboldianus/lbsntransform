# -*- coding: utf-8 -*-

"""Hll bases for social facet
"""

from typing import Tuple, Union

from lbsnstructure import lbsnstructure_pb2 as lbsn
from lbsntransform.output.hll import hll_bases as hll

from lbsntransform.output.hll.hll_functions import HLLFunctions as HLF

FACET = 'social'


class SocialBase(hll.HllBase):
    """Intermediate social base class that extends HllBase
    for common social base attributes
    """

    def __init__(self):
        super().__init__()
        self.metrics['latlng_hll'] = set()
        self.metrics['place_hll'] = set()
        self.metrics['date_hll'] = set()


class UserBase(SocialBase):
    """Extends Social Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='user')

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
    NAME = hll.HllBaseRef(facet=FACET, base='friends')

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
    NAME = hll.HllBaseRef(facet=FACET, base='community')

    def __init__(self, record: Union[lbsn.Origin, lbsn.Post] = None):
        super().__init__()
        self.attrs['name'] = None
        self.key['id'] = None
        if record is None:
            # init empty
            return
        if hasattr(record, "origin_id"):
            self.key['id'] = record.origin_id
            self.attrs['name'] = record.DESCRIPTOR.name
        else:
            self.key['id'] = record.pkey.origin.origin_id


class CultureBase(SocialBase):
    """Extends Social Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='culture')

    def __init__(self, record: lbsn.Language = None):
        super().__init__()
        self.key['id'] = None
        if record is None:
            # init empty
            return
        self.key['id'] = record.language_short
