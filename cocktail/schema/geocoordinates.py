#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .schematuples import Tuple
from .schemanumbers import Decimal


class GeoCoordinate(Decimal):
    pass


class Latitude(GeoCoordinate):
    pass


class Longitude(GeoCoordinate):
    pass


class GeoCoordinates(Tuple):

    def __init__(self, *args, **kwargs):
        kwargs["items"] = (
            Latitude("latitude", required = True),
            Longitude("longitude", required = True)
        )
        Tuple.__init__(self, *args, **kwargs)

