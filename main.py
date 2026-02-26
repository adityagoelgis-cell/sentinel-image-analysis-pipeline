import os

from src.ingestion import ingest_pipeline
from src.sentinel1_processing import (
    read_sar_band,
    apply_lee_filter,
    compute_glcm_texture,
    save_georeferenced_raster,
)
from src.sentinel2_processing import process_sentinel2
from src.utils import ensure_dir, log

def process_sentinel1(vv_files):
    """Process Sentinel-1 VV data and extract texture features."""
    results = []

    output_dir = "data/processed/sentinel1"
    ensure_dir(output_dir)

    for raster_path in vv_files:
        filename = os.path.basename(raster_path)
        log(f"Sentinel-1 processing: {filename}")

        try:
            log("Reading SAR data")
            sar = read_sar_band(raster_path)

            # Crop for faster texture computation
            sar = sar[:2000, :2000]

            log("Applying Lee filter")
            sar_filtered = apply_lee_filter(sar)

            output_path = os.path.join(
                output_dir,
                filename.replace(".tif", "_lee_filtered.tif")
            )

            log("Saving filtered SAR")
            save_georeferenced_raster(raster_path, output_path, sar_filtered)

            log("Computing GLCM texture")
            contrast, homogeneity = compute_glcm_texture(sar_filtered)

            results.append({
                "file": filename,
                "contrast": contrast,
                "homogeneity": homogeneity,
            })

        except Exception as exc:
            log(f"[ERROR] Sentinel-1 failed for {filename}: {exc}")
            results.append({
                "file": filename,
                "contrast": None,
                "homogeneity": None,
            })

    return results

def main():
    log("=== Image Analyst Processing Pipeline ===")

    data_root = "data/raw"
    ingestion_result = ingest_pipeline(data_root)

    # Sentinel-1
    s1_data = ingestion_result.get("sentinel1", {})
    vv_files = s1_data.get("VV", [])

    if vv_files:
        log(f"Found {len(vv_files)} Sentinel-1 VV file(s)")
        s1_results = process_sentinel1(vv_files)
    else:
        log("No Sentinel-1 VV files found")
        s1_results = []

    # Sentinel-2
    s2_data = ingestion_result.get("sentinel2", {})
    b04 = s2_data.get("B04", [])
    b08 = s2_data.get("B08", [])
    scl = s2_data.get("SCL", [])

    if b04 and b08 and scl:
        log("Sentinel-2 NDVI processing started")
        process_sentinel2(
            b04_path=b04[0],
            b08_path=b08[0],
            scl_path=scl[0],
            output_dir="data/processed/sentinel2",
        )
    else:
        log("Sentinel-2 data incomplete, skipping NDVI")

    log("=== Processing Summary ===")
    for res in s1_results:
        if res["contrast"] is not None:
            print(
                f"Sentinel-1 | {res['file']} | "
                f"Contrast={res['contrast']:.3f}, "
                f"Homogeneity={res['homogeneity']:.3f}"
            )
        else:
            print(f"Sentinel-1 | {res['file']} | FAILED")

    log("Pipeline execution complete")


if __name__ == "__main__":
    main()