from pathlib import Path
from functools import wraps
import time


import geopy.distance
from geopy import Point
from shapely.geometry import Polygon

NORTH_BEARING = 0
EAST_BEARING = 90
SOUTH_BEARING = 180
WEST_BEARING = 270


def parse_band_meta(band_meta_path: Path) -> dict[str, str]:
    meta = dict()

    content = open(band_meta_path, "r").read().split("\n")

    for line in content:
        split = line.split("=")
        if len(split) == 2:
            meta[split[0]] = split[1]
    
    return meta


def get_coords(band_meta_path: Path) -> dict[str, Point]:
    meta = parse_band_meta(band_meta_path)
    coords = dict()
    
    coords['center'] = Point(meta['SceneCenterLat'], meta['SceneCenterLon'])
    coords['upper_left'] = Point(meta['ImageULLat'], meta['ImageULLon'])
    coords['upper_right'] = Point(meta['ImageURLat'], meta['ImageURLon'])
    coords['lower_left'] = Point(meta['ImageLLLat'], meta['ImageLLLon'])
    coords['lower_right'] = Point(meta['ImageLRLat'], meta['ImageLRLon'])

    return coords


def get_calibration_constants(band_meta_path: Path) -> dict[str, float]:
    meta = parse_band_meta(band_meta_path)

    return {
        "HH": float(meta['Calibration_Constant_HH']),
        "HV": float(meta['Calibration_Constant_HV'])
    }


def get_bounding_box_coordinates(center: Point, half_side_distance: int) -> dict[str, Point]:
    north = geopy.distance.distance(half_side_distance).destination(point=center, bearing=NORTH_BEARING)
    upper_left = geopy.distance.distance(half_side_distance).destination(point=north, bearing=WEST_BEARING)

    south = geopy.distance.distance(half_side_distance).destination(point=center, bearing=SOUTH_BEARING)
    lower_right = geopy.distance.distance(half_side_distance).destination(point=south, bearing=EAST_BEARING)


    return {
        "upper_left": upper_left,
        "lower_right": lower_right,
    }


def check_bounding_boxes(parent: dict[str, Point], child: dict[str, Point], half_side_distance: int):

    def create_polygon(ul: Point, lr: Point, ur: Point | None = None, ll: Point | None = None) -> Polygon:
        if ur is None and ll is None:
            ur = Point(ul.latitude, lr.longitude)
            ll = Point(lr.latitude, ul.longitude)
        

        return Polygon([
            (ll.longitude, ll.latitude),
            (lr.longitude, ll.latitude),
            (ur.longitude, ur.latitude),
            (ul.longitude, ul.latitude),
            (ll.longitude, ll.latitude)
        ])
    
    child_polygon = create_polygon(child['upper_left'], child['lower_right'])
    parent_polygon = create_polygon(ul=parent['upper_left'], ur=parent['upper_right'], lr=parent['lower_right'], ll=parent['lower_left'])


    return parent_polygon.covers(child_polygon)

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"[TIMER] {func.__name__!r} took {end - start:.4f} seconds")
        return result
    return wrapper