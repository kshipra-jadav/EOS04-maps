import matplotlib.pyplot as plt
 
from constants import *
from utils import *
from sar_processing import *

import rasterio

calibration_constants = get_calibration_constants(BAND_META_PATH)




sigma0_hh = compute_sigma_naught(rasterio.open(HH_PATH).read(1), rasterio.open(LIA_PATH).read(1), calibration_constants['HH'])
sigma0_hv = compute_sigma_naught(rasterio.open(HV_PATH).read(1), rasterio.open(LIA_PATH).read(1), calibration_constants['HV'])


plt.figure(figsize=(10, 8))
plt.title("Sigma Naught HH")
plt.imshow(sigma0_hh, cmap='gray')
plt.axis('off')
plt.savefig("/home/faafdaa/Pictures/major/sigma_naught_hh.png", bbox_inches='tight', pad_inches=0.1)

plt.figure(figsize=(10, 8))
plt.title("Sigma Naught HV")
plt.imshow(sigma0_hv, cmap='gray')
plt.axis('off')
plt.savefig("/home/faafdaa/Pictures/major/sigma_naught_hv.png", bbox_inches='tight', pad_inches=0.1)

