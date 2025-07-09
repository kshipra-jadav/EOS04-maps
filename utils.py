import xml.etree.ElementTree as ET

from pathlib import Path

def get_coords_from_xml(xml_path: Path) -> dict[dict[float, float]]:      
    tree = ET.parse(xml_path)
    root = tree.getroot()

    tie_points = root.find("ImageAttributes").find("GeographicInformation").find("GeolocationGrid").findall("ImageTiePoint")
    print(tie_points)

