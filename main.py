import os
import glob
from pathlib import Path
from pprint import pp

import folium

from utils import *

BASE_DIR = Path.home() / "work" / "major" / "SAR Data" / "Level 2 Data EOS04"

product_xml = BASE_DIR / "product.xml"

coords = get_coords_from_xml(product_xml)
pp(coords)