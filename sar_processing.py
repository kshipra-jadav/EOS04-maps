from pathlib import Path
import os
import time
from typing import Literal

from utils import *
from constants import *

import rasterio
from rasterio.transform import xy
from rasterio.warp import transform
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde


calibration_constants = get_calibration_constants(BAND_META_PATH)



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


def get_latlon_from_raster(path):
    with rasterio.open(path) as src:
        height, width = src.height, src.width
        transform_matrix = src.transform

        # Create grid of row/col indices
        rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')

        # Get projected X, Y (easting, northing in meters)
        xs, ys = xy(transform_matrix, rows, cols)

        # Flatten to 1D
        xs_flat = np.array(xs).flatten()
        ys_flat = np.array(ys).flatten()

        # Convert to lat/lon
        lons, lats = transform(src.crs, "EPSG:4326", xs_flat, ys_flat)

        # Reshape back to 2D grid
        lon = np.array(lons).reshape((height, width))
        lat = np.array(lats).reshape((height, width))

    return lat, lon


def main():
    # sigma0_hh = compute_sigma_naught(HH_PATH, calibration_constants['HH'], type='HH', show_metrics=True)
    # sigma0_hv = compute_sigma_naught(HV_PATH, calibration_constants['HV'], type='HV', show_metrics=True)

    lat_hh, lon_hh = get_latlon_from_raster(HH_PATH)

    print(lat_hh, lon_hh)


if __name__ == '__main__':
    main()