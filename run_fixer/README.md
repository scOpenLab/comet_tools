# COMET run fixer

Script to register and merge two OME-TIFF files derived from interrupted COMET runs for which the original tiles are not available.
The registration is performed with palom: https://github.com/labsyspharm/palom

## Usage

From the command line:
```
python3 comet_fixer.py image1 image2 output_image
```

## Setup

Tested from a mamba/conda environment with python 3.11.

Requirements:
```
palom
dask
tifffile
ome_types
unidecode
```

## Input

The script expects three positional input parameters:
- Path to the first OME-TIFF file derived from the same interrupted COMET run.
- Path to the second OME-TIFF file derived from the same interrupted COMET run.
- Path to the output image, if the `.ome.tiff` extension is not present, the script adds it.

## Output

An OME-TIFF file with all the channels from the two files registered, and the run metadata from the first file.
The channel and cycle metadata from the second file are added to the ones from the first and written to the output.
The output OME-TIFF file can be read with:
-  COMET Horizon VIewer (proprietary): https://lunaphore.com/products/horizon/  
- [napari](https://napari.org/stable/) with the [napari-tiff](https://napari-hub.org/plugins/napari-tiff.html) plugin (open-source).

## TO-DO
Take as input a folder with an arbitrary number of images from the same run, instead of 2 files.
