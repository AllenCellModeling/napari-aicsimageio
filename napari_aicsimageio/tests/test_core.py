#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dask.array as da
import numpy as np
import pytest

from napari_aicsimageio import core

# Example files
PNG_FILE = "example.png"
GIF_FILE = "example.gif"
TIF_FILE = "s_1_t_1_c_1_z_1.tiff"
CZI_FILE = "s_1_t_1_c_1_z_1.czi"
OME_FILE = "s_1_t_1_c_1_z_1.ome.tiff"
MED_TIF_FILE = "s_1_t_10_c_3_z_1.tiff"
BIG_OME_FILE = "s_3_t_1_c_3_z_5.ome.tiff"
BIG_CZI_FILE = "s_3_t_1_c_3_z_5.czi"


@pytest.mark.parametrize(
    "filename, in_memory, expected_dtype, expected_shape, expected_channel_axis",
    [
        (PNG_FILE, True, np.ndarray, (1, 800, 537, 4), None),
        (GIF_FILE, True, np.ndarray, (1, 72, 268, 268, 4), None),
        (CZI_FILE, True, np.ndarray, (1, 1, 1, 325, 475), None),
        (CZI_FILE, False, da.core.Array, (1, 1, 1, 325, 475), None),
        (OME_FILE, True, np.ndarray, (1, 325, 475), None),
        (OME_FILE, False, da.core.Array, (1, 325, 475), None),
        (TIF_FILE, True, np.ndarray, (1, 325, 475), None),
        (TIF_FILE, False, da.core.Array, (1, 325, 475), None),
        ([CZI_FILE, CZI_FILE], True, np.ndarray, (2, 1, 1, 325, 475), None),
        ([CZI_FILE, CZI_FILE], False, da.core.Array, (2, 1, 1, 325, 475), None),
        (MED_TIF_FILE, False, da.core.Array, (1, 10, 3, 325, 475), None),
        (BIG_CZI_FILE, False, da.core.Array, (1, 1, 3, 3, 5, 325, 475), None),
        (BIG_OME_FILE, False, da.core.Array, (1, 3, 5, 3, 325, 475), None),
    ],
)
def test_reader(
    data_dir, filename, in_memory, expected_dtype, expected_shape, expected_channel_axis
):
    # Append filename(s) to resources dir
    if isinstance(filename, str):
        path = str(data_dir / filename)
    else:
        path = [str(data_dir / _path) for _path in filename]

    # Get reader
    reader = core.get_reader(path, in_memory)

    # Check callable
    assert callable(reader)

    # Get data
    layer_data = reader(path)

    # We only return one layer
    data, _, _ = layer_data[0]

    # Check layer data
    assert isinstance(data, expected_dtype)
    assert data.shape == expected_shape
