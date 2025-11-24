# COMET background subtraction

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

## Setup

Tested from a pip3 environment with python 3.11.

Requirements:
```
dask
tifffile
ome_types
unidecode
opencv
```

## Input

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
  
## Output

An OME-TIFF file with the subtracted background channels and updated metadata.

## TO-DO
Convert to a simple python script usable for batch processing.
