import os
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from src.utils import log


def read_band(raster_path: str):
    """Read a single-band Sentinel-2 raster."""
    with rasterio.open(raster_path) as src:
        band = src.read(1).astype(np.float32)
        profile = src.profile.copy()
    return band, profile


def calculate_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    """Compute NDVI."""
    return (nir - red) / (nir + red + 1e-6)


def generate_cloud_mask(scl: np.ndarray) -> np.ndarray:
    """Create cloud mask from SCL classes."""
    cloud_classes = [3, 8, 9, 10]
    return np.isin(scl, cloud_classes)


def resample_scl_to_match(
    scl: np.ndarray,
    scl_profile: dict,
    target_profile: dict
) -> np.ndarray:
    """Resample SCL (20m) to match 10m target grid."""
    resampled = np.zeros(
        (target_profile["height"], target_profile["width"]),
        dtype=np.uint8
    )

    reproject(
        source=scl,
        destination=resampled,
        src_transform=scl_profile["transform"],
        src_crs=scl_profile["crs"],
        dst_transform=target_profile["transform"],
        dst_crs=target_profile["crs"],
        resampling=Resampling.nearest
    )

    return resampled


def save_raster(reference_profile: dict, output_path: str, array: np.ndarray) -> None:
    """Save NDVI raster as GeoTIFF."""
    profile = reference_profile.copy()
    profile.update(
        driver="GTiff",
        dtype=rasterio.float32,
        count=1,
        compress="deflate",
        nodata=np.nan
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(array.astype(np.float32), 1)


def process_sentinel2(
    b04_path: str,
    b08_path: str,
    scl_path: str,
    output_dir: str
) -> str:
    """Compute cloud-masked NDVI from Sentinel-2 L2A data."""

    log("Reading Sentinel-2 bands")
    red, red_profile = read_band(b04_path)
    nir, _ = read_band(b08_path)
    scl, scl_profile = read_band(scl_path)

    log("Resampling SCL to 10m")
    scl_resampled = resample_scl_to_match(scl, scl_profile, red_profile)

    log("Computing NDVI")
    ndvi = calculate_ndvi(nir, red)

    log("Applying cloud mask")
    ndvi[generate_cloud_mask(scl_resampled)] = np.nan

    output_path = os.path.join(output_dir, "sentinel2_ndvi_cloudmasked.tif")
    save_raster(red_profile, output_path, ndvi)

    log("Sentinel-2 processing complete")
    return output_path