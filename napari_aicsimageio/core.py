#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import xarray as xr
from aicsimageio import AICSImage, exceptions, types
from aicsimageio.dimensions import DimensionNames
from qtpy.QtWidgets import QListWidget

# from napari import Viewer
import napari

###############################################################################

LayerData = Union[Tuple[types.ArrayLike, Dict[str, Any], str]]
PathLike = Union[str, List[str]]
ReaderFunction = Callable[[PathLike], List[LayerData]]

###############################################################################
# _get_viewer() function from https://github.com/napari/napari/issues/2202
# To provide access to the napari viewer to make the dock widget
# Copyright (c) 2021 Jonas Windhager
# Licensed under MIT License


# def _get_viewer() -> Optional[Viewer]:
#     import inspect

#     frame = inspect.currentframe().f_back
#     while frame:
#         instance = frame.f_locals.get("self")
#         if instance is not None and isinstance(instance, Viewer):
#             return instance
#         frame = frame.f_back
#     return None


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


# Function to handle multi-scene files.
def _get_scenes(img: AICSImage, in_memory: bool) -> None:
    # Create the list widget and populate with the scenes in the file
    list_widget = QListWidget()
    for i, scene in enumerate(img.scenes):
        list_widget.addItem(f"{i} -- {scene}")
    viewer = napari.current_viewer()
    viewer.window.add_dock_widget([list_widget], area="right", name="Scene Selector")

    # Function to create image layer from a scene selected in the list widget
    def open_scene(item):
        scene_text = item.text()
        scene_index = int(scene_text.split(" -- ")[0])
        img.set_scene(scene_index)
        if DimensionNames.MosaicTile in img.reader.dims.order:
            try:
                if in_memory:
                    data = img.reader.mosaic_xarray_data
                else:
                    data = img.reader.mosaic_xarray_dask_data

            # Catch reader does not support tile stitching
            except NotImplementedError:
                print(
                    "AICSImageIO: Mosaic tile stitching "
                    "not yet supported for this file format reader."
                )
        else:
            if in_memory:
                data = img.reader.xarray_data
            else:
                data = img.reader.xarray_dask_data
        meta = _get_meta(data, img)
        viewer.add_image(data, name=scene, metadata=meta, scale=meta["scale"])

    list_widget.currentItemChanged.connect(open_scene)
    return None


# Function to get Metadata to provide with data
def _get_meta(data, img):
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

    return meta


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

    # Check for multiple scenes
    if len(img.scenes) > 1:
        print(
            f"AICSImageIO: Image contains {len(img.scenes)} scenes. "
            f"Supporting more than the first scene is a work in progress. "
            f"Select a scene from the list widget. There may be dragons!"
        )
        # Launch the list widget
        _get_scenes(img, in_memory=in_memory)
        # Return an empty LayerData list; ImgLayers will be handled via the widget.
        # HT Jonas Windhager
        return [(None,)]
    else:
        data = _get_full_image_data(img, in_memory=in_memory)

        # Catch None data
        if data is None:
            return None
        else:
            meta = _get_meta(data, img)
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
