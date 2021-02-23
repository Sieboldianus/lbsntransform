# -*- coding: utf-8 -*-

"""Hll bases for spatial facet
"""

from typing import Union

from lbsnstructure import lbsnstructure_pb2 as lbsn
from lbsntransform.output.hll import hll_bases as hll
from lbsntransform.tools.helper_functions import HelperFunctions as HF

from lbsntransform.output.hll.hll_functions import HLLFunctions as HLF

FACET = 'spatial'


class LatLngBase(hll.HllBase):
    """Extends Base Class"""
    # base reference, eg.
    # e.g.: facet: temporal, base: date
    NAME = hll.HllBaseRef(facet=FACET, base='latlng')

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


class PlaceBase(hll.HllBase):
    """Extends HllBase Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='place')

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
            self.key['place_guid'] = record.pkey.id
            # self.key['place_guid'] = HLF.hll_concat(
            #     [coordinates.lat, coordinates.lng])
            self.attrs['geom_center'] = HF.return_ewkb_from_geotext(
                coordinates_geom)
            self.attrs['geom_area'] = HF.return_ewkb_from_geotext(
                HF.null_check(record.geom_area))
            self.attrs['name'] = record.name


class SpatialBase(hll.HllBase):
    """Intermediate spatial base class that extends HllBase
    for Place, City, Region and Country
    sharing common attributes
    """

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
    NAME = hll.HllBaseRef(facet=FACET, base='city')

    def __init__(self, record: lbsn.Post = None):
        super().__init__(record)
        # rename key accordingly
        self.key["city_guid"] = self.key.pop("guid")


class RegionBase(SpatialBase):
    """Extends Spatial Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='region')

    def __init__(self, record: lbsn.Post = None):
        super().__init__(record)
        # rename key accordingly
        self.key["region_guid"] = self.key.pop("guid")


class CountryBase(SpatialBase):
    """Extends Spatial Base Class"""
    NAME = hll.HllBaseRef(facet=FACET, base='country')

    def __init__(self, record: lbsn.Post = None):
        super().__init__(record)
        # rename key accordingly
        self.key["country_guid"] = self.key.pop("guid")
