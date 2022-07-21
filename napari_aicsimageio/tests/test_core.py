#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, Tuple, Type

import dask.array as da
import npe2
import numpy as np
import pytest

from napari_aicsimageio import core

if TYPE_CHECKING:
    from napari import Viewer
    from napari.types import ArrayLike
    from npe2._pytest_plugin import TestPluginManager

###############################################################################

PNG_FILE = "example.png"
GIF_FILE = "example.gif"
OME_TIFF = "pipeline-4.ome.tiff"
LIF_FILE = "tiled.lif"
CZI_FILE = "variable_scene_shape_first_scene_pyramid.czi"

###############################################################################


@pytest.mark.parametrize(
    "in_memory, expected_dtype",
    [
        (True, np.ndarray),
        (False, da.core.Array),
    ],
)
@pytest.mark.parametrize(
    "filename, expected_shape, expected_meta",
    [
        (PNG_FILE, (800, 537, 4), {"name": "Image:0", "rgb": True}),
        (GIF_FILE, (72, 268, 268, 4), {"name": "Image:0", "rgb": True}),
        (
            CZI_FILE,
            (3, 6183, 7705),
            {
                "name": [
                    "0 :: A1-A1 :: EGFP",
                    "0 :: A1-A1 :: mCher",
                    "0 :: A1-A1 :: PGC",
                ],
                "channel_axis": 0,
                "scale": (0.908210704883533, 0.908210704883533),
            },
        ),
        (
            OME_TIFF,
            (4, 65, 600, 900),
            {
                "name": [
                    "0 :: Image:0 :: Bright_2",
                    "0 :: Image:0 :: EGFP",
                    "0 :: Image:0 :: CMDRP",
                    "0 :: Image:0 :: H3342",
                ],
                "channel_axis": 0,
                "scale": (0.29, 0.10833333333333332, 0.10833333333333332),
            },
        ),
        (
            LIF_FILE,
            (4, 5622, 7666),
            {
                "name": [
                    "0 :: TileScan_002 :: Gray",
                    "0 :: TileScan_002 :: Red",
                    "0 :: TileScan_002 :: Green",
                    "0 :: TileScan_002 :: Cyan",
                ],
                "channel_axis": 0,
                "scale": (0.20061311154598827, 0.20061311154598827),
            },
        ),
    ],
)
def test_reader(
    resources_dir: Path,
    filename: str,
    in_memory: bool,
    expected_dtype: type,
    expected_shape: Tuple[int, ...],
    expected_meta: Dict[str, Any],
    npe2pm: "TestPluginManager",
) -> None:
    # Resolve filename to filepath
    if isinstance(filename, str):
        path = str(resources_dir / filename)

    # Get reader
    reader = core.get_reader(path, in_memory)

    # Check callable
    assert callable(reader)

    # Get data
    layer_data = reader(path)

    # We only return one layer
    if layer_data is not None:
        data, meta, _ = layer_data[0]  # type: ignore

        # Check layer data
        assert isinstance(data, expected_dtype)  # type: ignore
        assert data.shape == expected_shape  # type: ignore

        # Check meta
        meta.pop("metadata", None)
        assert meta == expected_meta  # type: ignore

        # confirm that this also works via npe2
        with npe2pm.tmp_plugin(package="napari-aicsimageio") as plugin:
            [via_npe2] = npe2.read([path], stack=False, plugin_name=plugin.name)
            assert via_npe2[0].shape == data.shape  # type: ignore


SINGLESCENE_FILE = "s_1_t_1_c_1_z_1.czi"
MULTISCENE_FILE = "s_3_t_1_c_3_z_5.czi"


@pytest.mark.parametrize(
    "in_memory, expected_dtype",
    [
        (True, np.ndarray),
        (False, da.core.Array),
    ],
)
@pytest.mark.parametrize(
    "filename, expected_shape",
    [
        (SINGLESCENE_FILE, (325, 475)),
        (MULTISCENE_FILE, (3, 5, 325, 475)),
    ],
)
def test_for_multiscene_widget(
    make_napari_viewer: Callable[..., "Viewer"],
    resources_dir: Path,
    filename: str,
    in_memory: bool,
    expected_dtype: Type["ArrayLike"],
    expected_shape: Tuple[int, ...],
) -> None:
    # Make a viewer
    viewer = make_napari_viewer()
    assert len(viewer.layers) == 0
    assert len(viewer.window._dock_widgets) == 0

    # Resolve filename to filepath
    if isinstance(filename, str):
        path = str(resources_dir / filename)

    # Get reader
    reader = core.get_reader(path, in_memory)

    if reader is not None:
        # Call reader on path
        reader(path)

        if len(viewer.window._dock_widgets) != 0:
            viewer.window._dock_widgets[f"{filename} :: Scenes"].widget().setCurrentRow(
                1
            )
            data = viewer.layers[0].data
            assert isinstance(data.data, expected_dtype)
            assert data.shape == expected_shape
        else:
            data, _, _ = reader(path)[0]
            assert isinstance(data, expected_dtype)
            assert data.shape == expected_shape
