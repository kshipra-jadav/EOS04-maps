import os
import glob
from pathlib import Path
from pprint import pp

from utils import *

BASE_DIR = Path.home() / "work" / "major" / "SAR Data" / "Level 2 Data EOS04"

band_meta = BASE_DIR / "BAND_META.txt"

center_lat, center_long = get_scene_center(band_meta)
print(center_lat, center_long)