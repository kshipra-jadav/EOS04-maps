import xml.etree.ElementTree as ET
from pathlib import Path
import math

import geopy.distance

def get_coords_from_xml(xml_path: Path) -> dict[dict[float, float]]:      
    tree = ET.parse(xml_path)
    root = tree.getroot()

    corners = root.find("ImageAttributes").find("GeographicInformation").find("MapProjection").find("MapCorners")

    coords = dict()

    for corner in corners:
        lat = corner.find("Latitude").text
        long = corner.find("Longitude").text
        
        coords[corner.tag] = {
            "lat": float(lat),
            "long": float(long)
        }
    
    return coords


def get_scene_center(band_meta_path: Path) -> tuple[float, float]:
    meta = dict()
    contents = open(band_meta_path, "r").read().split("\n")

    for line in contents:
        split = line.split("=")
        if len(split) == 2:
            meta[split[0]] = split[1]
    
    return float(meta['SceneCenterLat']), float(meta['SceneCenterLon'])


def get_bounding_box_coordinates(center: tuple[float, float], north_distance: int, south_distance: int, east_distance: int, west_distance: int) -> dict[dict[float, float]]:
    NORTH_BEARING = 0
    EAST_BEARING = 90
    SOUTH_BEARING = 180
    WEST_BEARING = 270

    north = geopy.distance.distance(north_distance).destination(point=center, bearing=NORTH_BEARING)
    upper_left = geopy.distance.distance(west_distance).destination(point=north, bearing=WEST_BEARING)

    south = geopy.distance.distance(south_distance).destination(point=center, bearing=SOUTH_BEARING)
    lower_right = geopy.distance.distance(east_distance).destination(point=south, bearing=EAST_BEARING)


    return {
        "upper_left": (upper_left.latitude, upper_left.longitude),
        "lower_right": (lower_right.latitude, lower_right.longitude),
    }