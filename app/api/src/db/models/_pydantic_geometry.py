# https://gist.github.com/la-mar/439bb675ea84a2bac308de1e35c37fa5

import logging
from enum import Enum
from typing import Dict, Optional, Union

import geoalchemy2.shape
from geoalchemy2 import WKBElement
from shapely.geometry import Point, shape
from shapely.geometry.base import BaseGeometry

logger = logging.getLogger(__name__)


class EPSG(int, Enum):
    WGS84 = 4326
    WEBM = 3857  # web-mercator: projected from WGS84


def shape_to_wkb(
    shape: Union[BaseGeometry, WKBElement], srid: EPSG = EPSG.WGS84
) -> Optional[WKBElement]:
    if isinstance(shape, BaseGeometry):
        return geoalchemy2.shape.from_shape(shape, srid=EPSG(srid).value)
    elif isinstance(shape, WKBElement):
        return shape
    else:
        return None


def wkb_to_shape(wkb: Union[WKBElement, BaseGeometry]) -> Optional[BaseGeometry]:
    if isinstance(wkb, WKBElement):
        return geoalchemy2.shape.to_shape(wkb)
    elif isinstance(wkb, BaseGeometry):
        return wkb
    else:
        return None


def create_geom(v, values) -> Point:
    if v is not None:
        try:
            if isinstance(v, list):
                return Point(*v)
            elif isinstance(v, dict):
                return shape(v)
            elif hasattr(v, "__geo_interface__"):
                pass  # v is already a geometry
            return v
        except Exception as e:
            logger.debug(f"Failed creating geom: v={v} -- {e}")
    else:
        try:
            lon = values.get("lon", None)
            lat = values.get("lat", None)
            if lon is not None and lat is not None:
                return Point(lon, lat)
            else:
                return None
        except Exception as e:
            logger.debug(f"Failed creating geom: v={v} -- {e}")


def dump_geom(cls, v) -> Dict:
    if isinstance(v, dict):
        return v
    else:
        return getattr(wkb_to_shape(v), "__geo_interface__", None)
