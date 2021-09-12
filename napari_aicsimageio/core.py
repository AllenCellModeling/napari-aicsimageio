#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import xarray as xr
from aicsimageio import AICSImage, exceptions, types
from aicsimageio.dimensions import DimensionNames
from qtpy.QtWidgets import QListWidget
from qtpy.QtCore import Qt
from napari import Viewer

###############################################################################

LayerData = Union[Tuple[types.ArrayLike, Dict[str, Any], str]]
PathLike = Union[str, List[str]]
ReaderFunction = Callable[[PathLike], List[LayerData]]

###############################################################################
# _get_viewer() function from https://github.com/napari/napari/issues/2202
# Copyright (c) 2021 Jonas Windhager
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
def _get_viewer() -> Optional[Viewer]:
    import inspect

    frame = inspect.currentframe().f_back
    while frame:
        instance = frame.f_locals.get("self")
        if instance is not None and isinstance(instance, Viewer):
            return instance
        frame = frame.f_back
    return None


###############################################################################


def _get_full_image_data(img: AICSImage, in_memory: bool) -> Optional[xr.DataArray]:
    if DimensionNames.MosaicTile in img.reader.dims.order:
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

    else:
        if in_memory:
            return img.reader.xarray_data
        else:
            return img.reader.xarray_dask_data

    return None


def _get_scenes(img: AICSImage, in_memory: bool) -> Optional[xr.DataArray]:
    list_widget = QListWidget()
    for scene in img.scenes:
        list_widget.addItem(scene)
    viewer = _get_viewer()
    # list_widget.currentItemChanged.connect(open_scene)
    viewer.window.add_dock_widget([list_widget], area="right")

    return None


def reader_function(
    path: PathLike, in_memory: bool, scene_name: Optional[str] = None
) -> Optional[List[LayerData]]:
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

    if len(img.scenes) > 1:
        print(
            f"AICSImageIO: Image contains {len(img.scenes)} scenes. "
            f"Supporting more than the first scene is a work in progress. "
            f"Will show scenes, but load scene: '{img.current_scene}'."
        )
        _get_scenes(img, in_memory=in_memory)
        data = _get_full_image_data(img, in_memory=in_memory)
    else:
        data = _get_full_image_data(img, in_memory=in_memory)

    # Catch None data
    if data is None:
        return None
    else:
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

        # Handle scales
        scale: List[float] = []
        for dim in img.reader.dims.order:
            if dim in [
                DimensionNames.SpatialX,
                DimensionNames.SpatialY,
                DimensionNames.SpatialZ,
            ]:
                scale_val = getattr(img.physical_pixel_sizes, dim)
                if scale_val is not None:
                    scale.append(scale_val)

        # Apply scales
        if len(scale) > 0:
            meta["scale"] = tuple(scale)

        # Apply all other metadata
        meta["metadata"] = {"ome_types": img.metadata}

        return [(data.data, meta, "image")]


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
        return partial(reader_function, in_memory=in_memory)  # type: ignore

    # No supported reader, return None
    except exceptions.UnsupportedFileFormatError:
        print("AICSImageIO: Unsupported file format.")
        return None

    except Exception as e:
        print("AICSImageIO: exception occurred during reading...")
        print(e)
        print(
            "If this issue looks like a problem with AICSImageIO, "
            "please file a bug report: "
            "https://github.com/AllenCellModeling/napari-aicsimageio"
        )
        return None
