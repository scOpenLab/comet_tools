#!/usr/bin/env python
# coding: utf-8

"""
Script to register and merge two OME-TIFF files from interrupted COMET runs.
The registration is performed with palom: https://github.com/labsyspharm/palom
"""

import argparse
import dask.array as da
import tifffile
import ome_types
from unidecode import (
    unidecode,
)
import palom


def get_arguments():
    """
    Parses and checks command line arguments, and provides an help text.
    Assumes 3 and returns 3 positional command line arguments:
    """
    parser = argparse.ArgumentParser(
        description="Aligns and combines images from an interrupted COMET run."
    )
    parser.add_argument(
        "first_image",
        help="path to the first image",
    )
    parser.add_argument(
        "second_image",
        help="path to the second image",
    )
    parser.add_argument(
        "output_path",
        help="path to the output OME-TIFF",
    )
    args = parser.parse_args()
    return (
        args.first_image,
        args.second_image,
        args.output_path,
    )


if __name__ == "__main__":
    (
        path1,
        path2,
        output_path,
    ) = get_arguments()

    OME_EXTENSION = ".ome.tiff"
    if not output_path.endswith(OME_EXTENSION):
        output_path += OME_EXTENSION

    print("Reading images")
    c1r = palom.reader.OmePyramidReader(path1)
    c2r = palom.reader.OmePyramidReader(path2)

    print("Coarse alignment")
    # `LEVEL = 0` for processing lowest level pyramid (full resolution)
    LEVEL = 0
    # select a higher pyramid level for feature-based affine registration as
    # initial coarse alignment (thumbnail level)
    THUMBNAIL_LEVEL = c1r.get_thumbnail_level_of_size(1000)

    c21l = palom.align.Aligner(
        ref_img=c1r.read_level_channels(
            LEVEL,
            0,
        ),
        moving_img=c2r.read_level_channels(
            LEVEL,
            0,
        ),
        ref_thumbnail=c1r.read_level_channels(
            THUMBNAIL_LEVEL,
            0,
        ).compute(),
        moving_thumbnail=c2r.read_level_channels(
            THUMBNAIL_LEVEL,
            0,
        ).compute(),
        ref_thumbnail_down_factor=c1r.level_downsamples[THUMBNAIL_LEVEL]
        / c1r.level_downsamples[LEVEL],
        moving_thumbnail_down_factor=c2r.level_downsamples[THUMBNAIL_LEVEL]
        / c2r.level_downsamples[LEVEL],
    )

    # run feature-based affine registration using thumbnails
    c21l.coarse_register_affine(
        n_keypoints=4000,
        plot_match_result=False,
    )

    print("Fine alignment")
    # after coarsly affine registered, run phase correlation on each of the
    # corresponding chunks (blocks/pieces) to refine translations
    c21l.compute_shifts()
    # discard incorrect shifts which is usually due to low contrast in the
    # background regions; this is needed for WSI but maybe not for ROI images
    c21l.constrain_shifts()

    print("Performing transformation on all channels")
    # configure the transformation for aligning the moving image
    # to the registration reference image
    c2m = palom.align.block_affine_transformed_moving_img(
        ref_img=c1r.read_level_channels(
            LEVEL,
            0,
        ),
        # select all the three channels (RGB) in moving image to transform
        moving_img=c2r.pyramid[LEVEL],
        mxs=c21l.block_affine_matrices_da,
    )

    print("Concatenating images:")
    # Concatenate the registered image to the first image (full resolution)
    img = da.concatenate(
        [
            c1r.pyramid[LEVEL],
            c2m,
        ],
        axis=0,
    )
    print(img.shape)

    print(f"Writing pyramidal OME-TIFF at {output_path}")
    palom.pyramid.write_pyramid(
        mosaics=[img],
        output_path=output_path,
        pixel_size=c1r.pixel_size * c1r.level_downsamples[LEVEL],
        save_RAM=False,
    )

    print("Collecting metadata.")
    # Reads the meatada from the first tiff file,
    # these will be copied to the registered OME-TIFF
    with tifffile.TiffFile(path1) as tif:
        ome_xml1 = tif.ome_metadata
    ome1 = ome_types.from_xml(ome_xml1)

    # Reads the meatada from the second tiff file,
    # these will be used to get channel and cycle metadata
    with tifffile.TiffFile(path2) as tif:
        ome_xml2 = tif.ome_metadata
    ome2 = ome_types.from_xml(ome_xml2)

    # Add channels from the other image to the first
    c1 = c1r.pyramid[LEVEL].shape[0]
    c2 = c2m.shape[0]
    for c in range(c2):
        ome2.images[0].pixels.channels[c].id = f"Channel:{c + c1}"
        ome2.images[0].pixels.planes[c].the_c = (
            c + c1
        )  # start from the end of the first image
    ome1.images[0].pixels.channels = (
        ome1.images[0].pixels.channels + ome2.images[0].pixels.channels
    )
    ome1.images[0].pixels.planes = (
        ome1.images[0].pixels.planes + ome2.images[0].pixels.planes
    )
    ome1.images[0].pixels.size_c = c1 + c2

    print("Channel metadata:")
    print(ome1.images[0].pixels.planes)

    # Add cycle metadata from the second image
    # to the COMET Horizon, structured annotation
    c1 = ome1.structured_annotations[0].value.any_elements[0].children
    c2 = ome2.structured_annotations[0].value.any_elements[0].children
    cycleid = int(c1[-1].attributes["CycleID"]) + 1
    channel = int(c1[-1].attributes["ID"].split(":")[-1]) + 1
    for c in c2:
        c.attributes["CycleID"] = str(int(c.attributes["CycleID"]) + cycleid)
        c.attributes["ID"] = "Channel:" + str(
            int(c.attributes["ID"].split(":")[-1]) + channel
        )
    ome1.structured_annotations[0].value.any_elements[0].children = c1 + c2

    print("Cycle metadata:")
    print(ome1.structured_annotations[0].value.any_elements[0].children)

    print("Writing metadata.")
    # Convert back to XML
    ome_xml = ome1.to_xml()
    ome_xml = unidecode(ome_xml)

    # Write the new XML metadata to the output file (overwrites)
    tifffile.tiffcomment(
        output_path,
        ome_xml,
    )

    print("DONE!")
