import os
import numpy as np
import rasterio
from scipy.ndimage import uniform_filter
from skimage.feature import graycomatrix, graycoprops


def read_sar_band(raster_path: str) -> np.ndarray:
    """Read single-band SAR raster as float32."""
    with rasterio.open(raster_path) as src:
        return src.read(1).astype(np.float32)


def apply_lee_filter(sar_array: np.ndarray, window_size: int = 7) -> np.ndarray:
    """Apply Lee speckle filter to SAR data."""
    local_mean = uniform_filter(sar_array, window_size)
    local_mean_sq = uniform_filter(sar_array ** 2, window_size)

    local_variance = local_mean_sq - local_mean ** 2
    global_variance = np.var(sar_array)

    weights = local_variance / (local_variance + global_variance)
    return (local_mean + weights * (sar_array - local_mean)).astype(np.float32)


def compute_glcm_texture(sar_array: np.ndarray) -> tuple[float, float]:
    """Compute basic GLCM texture metrics."""
    scaled = sar_array - np.nanmin(sar_array)
    scaled = scaled / np.nanmax(scaled)
    img_uint8 = (scaled * 255).astype(np.uint8)

    glcm = graycomatrix(
        img_uint8,
        distances=[1],
        angles=[0],
        levels=256,
        symmetric=True,
        normed=True
    )

    contrast = graycoprops(glcm, "contrast")[0, 0]
    homogeneity = graycoprops(glcm, "homogeneity")[0, 0]

    return float(contrast), float(homogeneity)


def save_georeferenced_raster(
    reference_raster: str,
    output_raster: str,
    data_array: np.ndarray
) -> None:
    """Save raster using CRS and transform from reference raster."""
    with rasterio.open(reference_raster) as src:
        profile = src.profile.copy()
        profile.update(
            driver="GTiff",
            dtype=rasterio.float32,
            count=1,
            height=data_array.shape[0],
            width=data_array.shape[1],
            transform=src.transform,
            crs=src.crs,
            nodata=np.nan,
            compress="deflate"
        )

    os.makedirs(os.path.dirname(output_raster), exist_ok=True)

    with rasterio.open(output_raster, "w", **profile) as dst:
        dst.write(data_array.astype(np.float32), 1)