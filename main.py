from utils import *
from pathlib import Path
from pprint import pp
from geopy import Point

from constants import *

coords = get_coords(BAND_META_PATH)

user_point = Point(23.2156, 72.6369)

bbox = get_bounding_box_coordinates(user_point, 25)

pp(coords)
pp(bbox)