# -*- coding: utf-8 -*-

"""
Shared structural elements
"""


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
    def lat_within_range(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude outside allowed range')
        return v

    @classmethod
    def lng_within_range(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude outside allowed range')
        return v
