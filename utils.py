import xml.etree.ElementTree as ET
from pathlib import Path

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

