from pathlib import Path
from typing import Literal

import rasterio.io
import rasterio.transform
import rasterio.warp


from utils import *
from constants import *

import rasterio
from rasterio.warp import transform
from rasterio.windows import from_bounds
import numpy as np
import matplotlib.pyplot as plt
from geopy import Point
import pandas as pd

calibration_constants = get_calibration_constants(BAND_META_PATH)

DEST_CRS = "EPSG:4326"

@timeit
def compute_sigma_naught(DN: np.ndarray, lia: np.ndarray, KBeta: float):
    '''
    sigma_naught = 10 * log_10(DN^2) + 10 * log_10(sin \theta_inc) - K_beta

    DN -> values from the HH or HV tif

    theta -> angle of incidence taken from lia.tif

    K_beta -> calibration constant

    '''
    DN = DN.astype(np.float32)
    lia = lia.astype(np.float32)

    theta_rad = np.radians(lia)

    mask_valid = (DN > 0) & (lia > 0) & (lia < 90)

    epsilon = 1e-10 # for div by 0 encounters

    sigma0 = np.full_like(DN, np.nan, dtype=float)

    sigma0[mask_valid] = (
        10 * np.log10((DN[mask_valid] ** 2)) +
        10 * np.log10(np.sin(theta_rad[mask_valid])) - 
        KBeta
    )


    return sigma0

@timeit
def crop_parent_raster_to_child(parent_raster: rasterio.io.DatasetReader, child_bbox: dict[str, Point]):
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
    new_transform = parent_raster.window_transform(window)

    return data, new_transform

@timeit
def get_latlon_from_raster(original_raster: rasterio.io.DatasetReader, original_raster_transform, original_raster_crs):
    height, width = original_raster.shape
    affine_transform = original_raster_transform

    rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    xs, ys = rasterio.transform.xy(affine_transform, rows, cols)

    lats, lons = rasterio.warp.transform(original_raster_crs, DEST_CRS, xs, ys)

    return lats, lons

@timeit
def make_dataset(raw_HH: np.ndarray, raw_HV: np.ndarray, sigma0_HH: np.ndarray, sigma0_HV: np.ndarray, lats: list, lons: list):
    '''
    Make dataset from the given values.
    The dataset will have 6 columns
    1. HH (sigma0) [dB]
    2. HV (sigma0) [dB]
    3. HH - HV (sigma0_HH - sigma0_HV) [dB]
    4. HH / HV (raw_HH / raw_HV)
    5. Latitude
    6. Longitude
    '''

    # Flattening the arrays for dataset
    raw_HH = raw_HH.flatten()
    raw_HV = raw_HV.flatten()
    sigma0_HH = sigma0_HH.flatten()
    sigma0_HV = sigma0_HV.flatten()

    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = np.where(raw_HV == 0, np.nan, raw_HH / raw_HV).flatten()
        
    diff = sigma0_HH - sigma0_HV
    data_dict = {
        "HH [dB]": sigma0_HH,
        "HV [dB]": sigma0_HV,
        "HH / HV": ratio,
        "HH - HV [dB]": diff,
        "Latitude": lats,
        "Longitude": lons
    }

    df = pd.DataFrame(data_dict)
    df.to_csv("dataset.csv", index=False)





def main():
    # ideal use case
    hh = rasterio.open(HH_PATH)
    hv = rasterio.open(HV_PATH)
    lia = rasterio.open(LIA_PATH)


    user_point = Point(23.2156, 72.6369) # Gandhinagar
    child_bbox = get_bounding_box_coordinates(user_point, 25)
    
    cropped_hh, hh_transform = crop_parent_raster_to_child(hh, child_bbox)
    cropped_hv, hv_transform = crop_parent_raster_to_child(hv, child_bbox)
    cropped_lia, lia_transform = crop_parent_raster_to_child(lia, child_bbox)


    sigma0_hh = compute_sigma_naught(cropped_hh, cropped_lia, calibration_constants['HH'])
    sigma0_hv = compute_sigma_naught(cropped_hv, cropped_lia, calibration_constants['HV'])
    lats, lons = get_latlon_from_raster(cropped_hh, hh_transform, hh.crs)

    print(f"{len(lats)=},\n{len(lons)=},\n{sigma0_hh.shape=},\n{sigma0_hv.shape=},\n{cropped_hh.shape=},\n{cropped_hv.shape=},\n{cropped_lia.shape=}", sep="\n")

    make_dataset(cropped_hh, cropped_hv, sigma0_hh, sigma0_hv, lats, lons)


if __name__ == '__main__':
    main()