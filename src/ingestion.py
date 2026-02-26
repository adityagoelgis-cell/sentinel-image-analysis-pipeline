import os
from typing import List, Dict, Tuple


RASTER_EXTENSIONS: Tuple[str, ...] = (".tif", ".tiff", ".jp2")


def discover_rasters(root_dir: str) -> List[str]:
    """
    Recursively discover raster files under a directory.
    """
    rasters: List[str] = []

    for root, _, files in os.walk(root_dir):
        for name in files:
            if name.lower().endswith(RASTER_EXTENSIONS):
                rasters.append(os.path.join(root, name))

    return rasters


def ingest_sentinel1_grd(sentinel1_dir: str) -> Dict[str, List[str]]:
    """
    Ingest Sentinel-1 GRD rasters and separate by polarization.
    """
    rasters = discover_rasters(sentinel1_dir)

    vv = [p for p in rasters if "grd" in p.lower() and "vv" in p.lower()]
    vh = [p for p in rasters if "grd" in p.lower() and "vh" in p.lower()]

    return {
        "VV": vv,
        "VH": vh,
    }


def ingest_sentinel2_l2a(sentinel2_dir: str) -> Dict[str, List[str]]:
    """
    Ingest Sentinel-2 L2A rasters required for NDVI and cloud masking.
    """
    rasters = discover_rasters(sentinel2_dir)

    red = [p for p in rasters if "_b04_" in p.lower()]
    nir = [p for p in rasters if "_b08_" in p.lower()]
    scl = [p for p in rasters if "_scl_" in p.lower()]

    return {
        "B04": red,
        "B08": nir,
        "SCL": scl,
    }


def ingest_pipeline(data_root: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Unified ingestion entry point.

    Expected structure:
    data_root/
        sentinel1/
        sentinel2/
    """
    sentinel1_path = os.path.join(data_root, "sentinel1")
    sentinel2_path = os.path.join(data_root, "sentinel2")

    result: Dict[str, Dict[str, List[str]]] = {}

    if os.path.isdir(sentinel1_path):
        result["sentinel1"] = ingest_sentinel1_grd(sentinel1_path)
    else:
        result["sentinel1"] = {}

    if os.path.isdir(sentinel2_path):
        result["sentinel2"] = ingest_sentinel2_l2a(sentinel2_path)
    else:
        result["sentinel2"] = {}

    return result