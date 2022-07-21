#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from functools import partial
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from aicsimageio import AICSImage, exceptions
from aicsimageio.dimensions import DimensionNames
from qtpy.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

if TYPE_CHECKING:
    import xarray as xr
    from napari.types import LayerData, PathLike, ReaderFunction

logger = getLogger(__name__)

###############################################################################

AICSIMAGEIO_CHOICES = "AICSImageIO Scene Management"
CLEAR_LAYERS_ON_SELECT = "Clear All Layers on New Scene Selection"
UNPACK_CHANNELS_TO_LAYERS = "Unpack Channels as Layers"

SCENE_LABEL_DELIMITER = " :: "

# Threshold above which to use out-of-memory loading
IN_MEM_THRESHOLD_PERCENT = 0.3
IN_MEM_THRESHOLD_SIZE_BYTES = 4e9  # 4GB
###############################################################################


def _get_full_image_data(
    img: AICSImage,
    in_memory: bool,
) -> xr.DataArray:
    if DimensionNames.MosaicTile in img.reader.dims.order:
        try:
            if in_memory:
                return img.reader.mosaic_xarray_data.squeeze()

            return img.reader.mosaic_xarray_dask_data.squeeze()

        # Catch reader does not support tile stitching
        except NotImplementedError:
            logger.warning(
                "AICSImageIO: Mosaic tile stitching "
                "not yet supported for this file format reader."
            )

    if in_memory:
        return img.reader.xarray_data.squeeze()

    return img.reader.xarray_dask_data.squeeze()


# Function to get Metadata to provide with data
def _get_meta(data: xr.DataArray, img: AICSImage) -> Dict[str, Any]:
    meta: Dict[str, Any] = {}
    if DimensionNames.Channel in data.dims:
        # Construct basic metadata
        channels_with_scene_index = [
            f"{img.current_scene_index}{SCENE_LABEL_DELIMITER}"
            f"{img.current_scene}{SCENE_LABEL_DELIMITER}{channel_name}"
            for channel_name in data.coords[DimensionNames.Channel].data.tolist()
        ]
        meta["name"] = channels_with_scene_index
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
    img_meta = {"aicsimage": img, "raw_image_metadata": img.metadata}
    try:
        img_meta["ome_types"] = img.ome_metadata
    except Exception:
        pass

    meta["metadata"] = img_meta
    return meta


def _widget_is_checked(widget_name: str) -> bool:
    import napari

    # Get napari viewer from current process
    viewer = napari.current_viewer()

    # Get scene management widget
    scene_manager_choices_widget = viewer.window._dock_widgets[AICSIMAGEIO_CHOICES]
    for child in scene_manager_choices_widget.widget().children():
        if isinstance(child, QCheckBox):
            if child.text() == widget_name:
                return child.isChecked()

    return False


# Function to handle multi-scene files.
def _get_scenes(path: "PathLike", img: AICSImage, in_memory: bool) -> None:
    import napari

    # Get napari viewer from current process
    viewer = napari.current_viewer()

    # Add a checkbox widget if not present
    if AICSIMAGEIO_CHOICES not in viewer.window._dock_widgets:
        # Create a checkbox widget to set "Clear On Scene Select" or not
        scene_clear_checkbox = QCheckBox(CLEAR_LAYERS_ON_SELECT)
        scene_clear_checkbox.setChecked(False)

        # Create a checkbox widget to set "Unpack Channels" or not
        channel_unpack_checkbox = QCheckBox(UNPACK_CHANNELS_TO_LAYERS)
        channel_unpack_checkbox.setChecked(False)

        # Add all scene management state to a single box
        scene_manager_group = QGroupBox()
        scene_manager_group_layout = QVBoxLayout()
        scene_manager_group_layout.addWidget(scene_clear_checkbox)
        scene_manager_group_layout.addWidget(channel_unpack_checkbox)
        scene_manager_group.setLayout(scene_manager_group_layout)
        scene_manager_group.setFixedHeight(100)

        viewer.window.add_dock_widget(
            scene_manager_group,
            area="right",
            name=AICSIMAGEIO_CHOICES,
        )

    # Create the list widget and populate with the ids & scenes in the file
    list_widget = QListWidget()
    for i, scene in enumerate(img.scenes):
        list_widget.addItem(f"{i}{SCENE_LABEL_DELIMITER}{scene}")

    # Add this files scenes widget to viewer
    viewer.window.add_dock_widget(
        list_widget,
        area="right",
        name=f"{Path(path).name}{SCENE_LABEL_DELIMITER}Scenes",
    )

    # Function to create image layer from a scene selected in the list widget
    def open_scene(item: QListWidgetItem) -> None:
        scene_text = item.text()

        # Use scene indexes to cover for duplicate names
        scene_index = int(scene_text.split(SCENE_LABEL_DELIMITER)[0])

        # Update scene on image and get data
        img.set_scene(scene_index)
        data = _get_full_image_data(img=img, in_memory=in_memory)

        # Get metadata and add to image
        meta = _get_meta(data, img)

        # Optionally clear layers
        if _widget_is_checked(CLEAR_LAYERS_ON_SELECT):
            viewer.layers.clear()

        # Optionally remove channel axis
        if not _widget_is_checked(UNPACK_CHANNELS_TO_LAYERS):
            meta["name"] = scene_text
            meta.pop("channel_axis", None)

        viewer.add_image(data, **meta)

    list_widget.currentItemChanged.connect(open_scene)  # type: ignore


def reader_function(
    path: "PathLike", in_memory: Optional[bool] = None
) -> Optional[List["LayerData"]]:
    """
    Given a single path return a list of LayerData tuples.
    """
    # Only support single path
    if isinstance(path, list):
        logger.info("AICSImageIO: Multi-file reading not yet supported.")
        return None

    if in_memory is None:
        from aicsimageio.utils.io_utils import pathlike_to_fs
        from psutil import virtual_memory

        fs, path = pathlike_to_fs(path)
        imsize = fs.size(path)
        available_mem = virtual_memory().available
        _in_memory = (
            imsize <= IN_MEM_THRESHOLD_SIZE_BYTES
            and imsize / available_mem <= IN_MEM_THRESHOLD_PERCENT
        )
    else:
        _in_memory = in_memory

    # Alert console of how we are loading the image
    logger.info(f"AICSImageIO: Reader will load image in-memory: {_in_memory}")

    # Open file and get data
    img = AICSImage(path)

    # Check for multiple scenes
    if len(img.scenes) > 1:
        logger.info(
            f"AICSImageIO: Image contains {len(img.scenes)} scenes. "
            f"Supporting more than the first scene is experimental. "
            f"Select a scene from the list widget. There may be dragons!"
        )
        # Launch the list widget
        _get_scenes(path=path, img=img, in_memory=_in_memory)

        # Return an empty LayerData list; ImgLayers will be handled via the widget.
        # HT Jonas Windhager
        return [(None,)]
    else:
        data = _get_full_image_data(img, in_memory=_in_memory)
        meta = _get_meta(data, img)
        return [(data.data, meta, "image")]


def get_reader(
    path: "PathLike", in_memory: Optional[bool] = None
) -> Optional["ReaderFunction"]:
    """
    Given a single path or list of paths, return the appropriate aicsimageio reader.
    """
    # Only support single path
    if isinstance(path, list):
        logger.info("AICSImageIO: Multi-file reading not yet supported.")
        return None

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
        logger.warning("AICSImageIO: Unsupported file format.")
        return None

    except Exception as e:
        logger.warning("AICSImageIO: exception occurred during reading...")
        logger.warning(e)
        logger.warning(
            "If this issue looks like a problem with AICSImageIO, "
            "please file a bug report: "
            "https://github.com/AllenCellModeling/napari-aicsimageio"
        )
        return None
