from pathlib import Path
import os
import time
from typing import Literal

import rasterio.io

from utils import *
from constants import *

import rasterio
from rasterio.transform import xy
from rasterio.warp import transform
from rasterio.windows import from_bounds
import numpy as np
import matplotlib.pyplot as plt
from geopy import Point

calibration_constants = get_calibration_constants(BAND_META_PATH)

DEST_CRS = "EPSG:4326"

def compute_sigma_naught(DN_path: Path, KBeta: float, type: Literal['HH', 'HV'], show_metrics=False):
    '''
    sigma_naught = 10 * log_10(DN^2) + 10 * log_10(sin \theta_inc) - K_beta

    DN -> values from the HH or HV tif

    theta -> angle of incidence taken from lia.tif

    K_beta -> calibration constant

    '''

    # cache check
    if os.path.isdir(CACHE_DIR):
        if type == 'HH':
            if os.path.isfile(CACHE_HH):
                sigma0 = np.load(CACHE_HH, allow_pickle=True)
                return sigma0
        if type == 'HV':
            if os.path.isfile(CACHE_HV):
                sigma0 = np.load(CACHE_HV, allow_pickle=True)
                return sigma0


    read_time = time.perf_counter()
    DN = rasterio.open(DN_path).read(1).astype(float)
    lia = rasterio.open(LIA_PATH).read(1).astype(float)
    if show_metrics:
        print(f"TIF File Reading Took - {time.perf_counter() - read_time:.3f}s\n")

    theta_rad = np.radians(lia)

    mask_valid = (DN > 0) & (lia > 0) & (lia < 90)

    sigma0 = np.full_like(DN, np.nan, dtype=float)

    compute_time = time.perf_counter()
    sigma0[mask_valid] = (
        10 * np.log10(DN[mask_valid] ** 2) +
        10 * np.log10(np.sin(theta_rad[mask_valid])) - 
        KBeta
    )
    if show_metrics:
        print(f"Sigma0 Compute Time Took - {time.perf_counter() - compute_time:.3f}s\n")


    os.makedirs(CACHE_DIR, exist_ok=True)

    if type == 'HH':
        np.save(CACHE_HH, sigma0)
        print(f"New Cache Saved At - f{CACHE_HH}")
    if type == 'HV':
        np.save(CACHE_HV, sigma0)
        print(f"New Cache Saved At - f{CACHE_HV}")

    return sigma0


def crop_parent_raster_to_child(parent_raster_path: Path, child_bbox: dict[str, Point]):
    parent_raster = rasterio.open(parent_raster_path)

    ul_child, lr_child = child_bbox['upper_left'], child_bbox['lower_right']

    # here, the CRS values for parent and child would be different.
    # hence, we will be converting the child who are in lats, lons to the parent's CRS which is in meteres [easting, northing, ...
    # and we get a meters reprerentation of the child's bounding box
    xs, ys = transform(DEST_CRS, parent_raster.crs, (ul_child.longitude, lr_child.longitude), (ul_child.latitude, lr_child.latitude))

    # now we create a window using the same meters representation of the child's bounding box
    window = from_bounds(
        left=min(xs),
        right=max(xs),
        bottom=min(ys),
        top=max(ys),
        transform=parent_raster.transform
    )

    # now we read from the parent raster but only confined to the window that we created earlier
    data = parent_raster.read(1, window=window)

    return data




def main():
    # sigma0_hh = compute_sigma_naught(HH_PATH, calibration_constants['HH'], type='HH', show_metrics=True)
    # sigma0_hv = compute_sigma_naught(HV_PATH, calibration_constants['HV'], type='HV', show_metrics=True)

    lat_hh, lon_hh = get_latlon_from_raster(HH_PATH)

    print(lat_hh, lon_hh)


if __name__ == '__main__':
    main()