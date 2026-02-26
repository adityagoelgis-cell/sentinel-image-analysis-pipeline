# Image Analyst Processing Pipeline  
**Sentinel-1 SAR & Sentinel-2 Optical Analysis**

## Overview
This project implements an end-to-end image analysis pipeline for **Sentinel-1 GRD (SAR)** and **Sentinel-2 L2A (optical)** satellite data using Python and open-source geospatial libraries.

The pipeline focuses on:
- SAR speckle reduction and texture analysis (Sentinel-1)
- NDVI computation with cloud masking (Sentinel-2)
- Proper handling of raster metadata (CRS and geotransform)
- GIS-ready outputs compatible with QGIS and SNAP

---

## Directory Structure

```text
imageAnalystPipeline/
│
├── data/
│   ├── raw/
│   │   ├── sentinel1/
│   │   └── sentinel2/
│   └── processed/
│       ├── sentinel1/
│       └── sentinel2/
│
├── src/
│   ├── ingestion.py
│   ├── sentinel1_processing.py
│   ├── sentinel2_processing.py
│   └── utils.py
│
├── main.py
├── requirements.txt
└── README.md
````

---

## Sentinel-1 Processing (SAR)

### Input

* Sentinel-1 GRD VV polarization rasters
* Data assumed to originate from Sentinel-1 SAFE products

### Processing Steps

* Automatic ingestion and polarization separation
* Lee speckle filtering
* GLCM texture extraction (Contrast, Homogeneity)
* Export of filtered SAR as GeoTIFF with preserved CRS

### Output

* Filtered SAR raster (`*_lee_filtered.tif`)
* Console summary of texture metrics

---

## Sentinel-2 Processing (Optical)

### Input

* Sentinel-2 L2A products:

  * B04 (Red, 10 m)
  * B08 (NIR, 10 m)
  * SCL (Scene Classification Layer, 20 m)

### Processing Steps

* Band loading from JP2
* NDVI computation
  [
  NDVI = \frac{NIR - Red}{NIR + Red}
  ]
* Cloud masking using SCL classes (3, 8, 9, 10)
* SCL resampling from 20 m to 10 m
* NDVI export as GeoTIFF (float32, NoData = NaN)

### Output

* `sentinel2_ndvi_cloudmasked.tif`

---

## Validation

### Sentinel-1

* Visual comparison of raw vs filtered SAR
* Reduced speckle with preserved spatial patterns
* GLCM metrics confirm increased homogeneity
* Validation performed in QGIS and SNAP

### Sentinel-2

* NDVI values verified within range [-1, +1]
* Pixel-level inspection using QGIS Identify Tool
* Histogram analysis confirms realistic vegetation distribution
* Cloud-masked pixels appear as NoData

---

## Georeferencing Notes

* Output rasters preserve CRS and affine transform from reference inputs
* Sentinel-1 GRD data requires terrain correction for precise GIS alignment
* SNAP used for inspection of Sentinel products
* QGIS used for numeric and visual validation

---

## Environment Setup

It is recommended to run the pipeline inside a Python virtual environment.

```bash
python -m venv venv
```

### Activate the environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## How to Run

```bash
python main.py
```

The pipeline:

* Reads Sentinel-1 and Sentinel-2 data placed manually in `data/raw/`
* Processes available datasets
* Writes outputs to `data/processed/`

---

## Dependencies

Primary libraries used:

* rasterio
* numpy
* scipy
* scikit-image
* GDAL

All dependencies are listed in `requirements.txt`.

