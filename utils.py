import xml.etree.ElementTree as ET
from pathlib import Path
import math

import geopy.distance
from geopy import Point

def get_coords(base_meta_path: Path) -> dict[str, Point]:      
    meta = dict()
    coords = dict()
    
    contents = open(base_meta_path, "r").read().split("\n")

    for line in contents:
        split = line.split("=")
        if len(split) == 2:
            meta[split[0]] = split[1]
    
    coords['center'] = Point(meta['SceneCenterLat'], meta['SceneCenterLon'])
    coords['upper_left'] = Point(meta['ImageULLat'], meta['ImageULLon'])
    coords['upper_right'] = Point(meta['ImageURLat'], meta['ImageURLon'])
    coords['lower_left'] = Point(meta['ImageLLLat'], meta['ImageLLLon'])
    coords['lower_right'] = Point(meta['ImageLRLat'], meta['ImageLRLon'])

    return coords


def get_bounding_box_coordinates(center: Point, half_side_distance: int) -> dict[str, Point]:
    NORTH_BEARING = 0
    EAST_BEARING = 90
    SOUTH_BEARING = 180
    WEST_BEARING = 270

    north = geopy.distance.distance(half_side_distance).destination(point=center, bearing=NORTH_BEARING)
    upper_left = geopy.distance.distance(half_side_distance).destination(point=north, bearing=WEST_BEARING)

    south = geopy.distance.distance(half_side_distance).destination(point=center, bearing=SOUTH_BEARING)
    lower_right = geopy.distance.distance(half_side_distance).destination(point=south, bearing=EAST_BEARING)


    return {
        "upper_left": upper_left,
        "lower_right": lower_right,
    }