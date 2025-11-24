# COMET TOOLS
Repository with a collection of tools for working with [COMET](https://lunaphore.com/products/comet/?utm_term=akoya%20phenoptics&utm_campaign=Competitors&utm_source=adwords&utm_medium=ppc&hsa_acc=1564322435&hsa_cam=14646038297&hsa_grp=130154601794&hsa_ad=545615703075&hsa_src=g&hsa_tgt=kwd-1395904984928&hsa_kw=akoya%20phenoptics&hsa_mt=b&hsa_net=adwords&hsa_ver=3&gad_source=1&gad_campaignid=14646038297&gclid=Cj0KCQiAoZDJBhC0ARIsAERP-F-SksPJaZqq2MAjO8n1HOdyVxtkPFgtCDOqovidHjodrnmfa69ys20aAsVeEALw_wcB) imaging data.

## Contents:
- [**COMET background subtraction**](https://github.com/scOpenLab/comet_tools/tree/main/background_sutraction)
- [**COMET run fixer**](https://github.com/scOpenLab/comet_tools/tree/main/run_fixer)

## COMET background subtraction

Notebook for performing background subtraction from original raw COMET ome.tiff files
the notebook uses the same [Normalized Subtraction formula](https://lunaphore.com/resource-center/technical-notes/comet-how-to-reduce-and-remove-autofluorescence/) used by the HORIZON software (see user manual),
and the resulting images are equivalent. 
```
The method available in HORIZON for background subtraction is Normalized Subtraction
which applies the following transformation to the pixels of the channel:
𝑃𝑆 = 𝑃𝑂 − (𝑃𝐵 × 𝐸𝑂) / 𝐸𝐵
With P the pixel value, E the exposure time, S the subtracted channel, O the original 
channel and B the background channel
```
The original metadata are rewritten to the image to mantain
compatibility with the horizon software.

### Setup

Tested from a pip3 environment with python 3.11.

Requirements:
```
dask
tifffile
ome_types
unidecode
opencv
```

### Input

The notebook expects three input parameters:
- Path to the raw .ome.tiff COMET file.
- Path to the output image
- Dictionary describing the background subtraction operations:

Define the subtraction channels:
```
{
  "NEW_CHANNEL_NAME": ("RAW_CHANNEL", "BG_CHANNEL"|None),
  ...  
}
```
If the background channel is None, then the raw channel is rewritten as is
Only channels mentioned in the dictionary are included in the output
E.g. to include the original background channels add them in the dict with the
background channel set to None
  
### Output

An OME-TIFF file with the subtracted background channels and updated metadata.

### TO-DO
Convert to a simple python script usable for batch processing.



## COMET run fixer

Script to register and merge two OME-TIFF files derived from interrupted COMET runs for which the original tiles are not available.
The registration is performed with palom: https://github.com/labsyspharm/palom

### Usage

From the command line:
```
python3 comet_fixer.py image1 image2 output_image
```

### Setup

Tested from a mamba/conda environment with python 3.11.

Requirements:
```
palom
dask
tifffile
ome_types
unidecode
```

### Input

The script expects three positional input parameters:
- Path to the first OME-TIFF file derived from the same interrupted COMET run.
- Path to the second OME-TIFF file derived from the same interrupted COMET run.
- Path to the output image, if the `.ome.tiff` extension is not present, the script adds it.

### Output

An OME-TIFF file with all the channels from the two files registered, and the run metadata from the first file.
The channel and cycle metadata from the second file are added to the ones from the first and written to the output.
The output OME-TIFF file can be read with:
-  COMET Horizon VIewer (proprietary): https://lunaphore.com/products/horizon/  
- [napari](https://napari.org/stable/) with the [napari-tiff](https://napari-hub.org/plugins/napari-tiff.html) plugin (open-source).

### TO-DO
Take as input a folder with an arbitrary number of images from the same run, instead of 2 files.

