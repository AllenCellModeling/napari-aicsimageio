#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Any, Dict, Tuple

import dask.array as da
import numpy as np
import pytest

from napari_aicsimageio import core

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
                "name": ["EGFP", "mCher", "PGC"],
                "channel_axis": 0,
                "scale": (9.08210704883533, 9.08210704883533),
            },
        ),
        (
            OME_TIFF,
            (1, 4, 65, 600, 900),
            {
                "name": ["Bright_2", "EGFP", "CMDRP", "H3342"],
                "channel_axis": 1,
                "scale": (0.29, 0.10833333333333332, 0.10833333333333332),
            },
        ),
        (
            LIF_FILE,
            (1, 4, 1, 5622, 7666),
            {
                "name": ["Gray", "Red", "Green", "Cyan"],
                "channel_axis": 1,
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
    "filename, nr_widgets, expected_shape",
    [
        (SINGLESCENE_FILE, 0, (1, 325, 475)),
        (MULTISCENE_FILE, 1, (3, 5, 325, 475)),
    ],
)
def test_for_multiscene_widget(
    make_napari_viewer,
    resources_dir: Path,
    filename: str,
    in_memory: bool,
    nr_widgets: int,
    expected_dtype: type,
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

    # Call reader on path
    reader(path)

    # Check for list widget
    assert len(viewer.window._dock_widgets) == nr_widgets

    if len(viewer.window._dock_widgets) != 0:
        assert list(viewer.window._dock_widgets.keys())[0] == "Scene Selector"
        viewer.window._dock_widgets["Scene Selector"].widget().setCurrentRow(1)
        data = viewer.layers[0].data
        assert isinstance(data.data, expected_dtype)
        assert data.shape == expected_shape
    else:
        data, meta, _ = reader(path)[0]
        assert isinstance(data, expected_dtype)
        assert data.shape == expected_shape
