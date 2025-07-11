from utils import *
from pathlib import Path
from pprint import pp
from geopy import Point

from constants import *

coords = get_coords(BAND_META_PATH)

user_point = Point(22.3039, 70.8022)

bbox = get_bounding_box_coordinates(user_point, 25)

check_bounding_boxes(parent=coords, child=bbox, half_side_distance=25)