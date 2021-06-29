#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import xarray as xr
from aicsimageio import AICSImage, exceptions
from aicsimageio.dimensions import DimensionNames

###############################################################################

LayerData = Union[Tuple[Any], Tuple[Any, Dict], Tuple[Any, Dict, str]]
PathLike = Union[str, List[str]]
ReaderFunction = Callable[[PathLike], List[LayerData]]

###############################################################################

def _get_full_image_data(img: AICSImage, in_memory: bool) -> xr.DataArray:
    if (DimensionNames.MosaicTile in img.reader.dims.order):
        try:
            if in_memory:
                return img.reader.mosaic_xarray_data
            else:
                return img.reader.mosaic_xarray_dask_data

        # Catch reader does not support tile stitching
        except NotImplementedError:
            print(
                "AICSImageIO: Mosaic tile stitching "
                "not yet supported for this file format reader."
            )
            return None

    else:
        if in_memory:
            return img.reader.xarray_data
        else:
            return img.reader.xarray_dask_data

def _get_meta(img: AICSImage) -> Any:
    """
    This return type should change in the future to always return OME from ome-types.
    """
    return img.metadata

def reader_function(path: PathLike, in_memory: bool, scene_name: Optional[str] = None) -> List[LayerData]:
    """
    Given a single path return a list of LayerData tuples.
    """
    # Alert console of how we are loading the image
    print(f"AICSImageIO: Reader will load image in-memory: {in_memory}")

    # Only support single path
    if isinstance(path, list):
        print("AICSImageIO: Multi-file reading not yet supported.")
        return None

    # Open file and get data
    img = AICSImage(path)
    print(
        f"AICSImageIO: Image contains {len(img.scenes)} scenes. "
        f"napari-aicsimageio currently only supports loading first scene, "
        f"will load scene: '{img.current_scene}'."
    )

    data = _get_full_image_data(img, in_memory=in_memory)

    # Metadata to provide with data
    meta = {}
    if DimensionNames.Channel in data.dims:
        # Construct basic metadata
        meta["name"] = data.coords[DimensionNames.Channel].data.tolist()
        meta["channel_axis"] = data.dims.index(DimensionNames.Channel)
    
    # Not multi-channel, use current scene as image name
    else:
        meta["name"] = img.reader.current_scene

    # Handle samples / RGB
    if DimensionNames.Samples in img.reader.dims.order:
        meta["rgb"] = True
    
    # Apply all other metadata
    meta_reader = partial(_get_meta, img=img)
    meta["metadata"] = meta_reader

    return [(data, meta, "image")]


def get_reader(path: PathLike, in_memory: bool) -> Optional[ReaderFunction]:
    """
    Given a single path or list of paths, return the appropriate aicsimageio reader.
    """
    # Only support single path
    if isinstance(path, list):
        print("AICSImageIO: Multi-file reading not yet supported.")

    # See if there is a supported reader for the file(s) provided
    try:
        # There is an assumption that the images are stackable and
        # I think it is also safe to assume that if stackable, they are of the same type
        # So only determine reader for the first one
        AICSImage.determine_reader(path)

        # The above line didn't error so we know we have a supported reader
        # Return a partial function with in_memory determined
        return partial(reader_function, in_memory=in_memory)

    # No supported reader, return None
    except exceptions.UnsupportedFileFormatError:
        print("AICSImageIO: Unsupported file format.")
