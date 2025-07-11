from pathlib import Path

DIR_NAME = "E04_SAR_MRS_19JUN2025_170130832927_18468_STUC00ZTD_25091_5_DH_A_R_N23740_E072155"

BASE_DIR = Path.home() / "work" / "major" / "SAR Data" / "Map Test Data" / DIR_NAME

IMG_PATH = BASE_DIR / "E04_SAR_MRS_19JUN2025_170130832927_18468_STUC00ZTD_25091_5_DH_A_R_N23740_E072155.jpg"

BAND_META_PATH = BASE_DIR / "BAND_META.txt"

HH_PATH = BASE_DIR / "scene_HH" / "imagery_HH.tif"
HV_PATH = BASE_DIR / "scene_HV" / "imagery_HV.tif"
LIA_PATH = BASE_DIR / f"{DIR_NAME}_lia.tif"
CACHE_DIR = Path.cwd() / "cache"
CACHE_HH = CACHE_DIR / "sigma0_HH.npy"
CACHE_HV = CACHE_DIR / "sigma0_HV.npy"