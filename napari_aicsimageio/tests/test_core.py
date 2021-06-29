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
            {"name": ["EGFP", "mCher", "PGC"], "channel_axis": 0},
        ),
        (
            OME_TIFF,
            (1, 4, 65, 600, 900),
            {"name": ["Bright_2", "EGFP", "CMDRP", "H3342"], "channel_axis": 1},
        ),
        (
            LIF_FILE,
            (1, 4, 1, 5622, 7666),
            {"name": ["Gray", "Red", "Green", "Cyan"], "channel_axis": 1},
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
