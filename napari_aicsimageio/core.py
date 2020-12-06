#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import dask.array as da
import numpy as np
from aicsimageio import AICSImage, exceptions
from aicsimageio.constants import Dimensions

###############################################################################

LayerData = Union[Tuple[Any], Tuple[Any, Dict], Tuple[Any, Dict, str]]
PathLike = Union[str, List[str]]
ReaderFunction = Callable[[PathLike], List[LayerData]]

###############################################################################


def reader_function(path: PathLike, in_memory: bool) -> List[LayerData]:
    """
    Given a single path return a list of LayerData tuples.
    """
    # Alert console of how we are loading the image
    print(f"Reader will load image in-memory: {in_memory}")

    # Standardize path to list of paths
    paths = [path] if isinstance(path, str) else path

    # Determine reader for all
    ReaderClass = AICSImage.determine_reader(paths[0])

    # Create readers for each path
    readers = [ReaderClass(path) for path in paths]

    # Read every file or create delayed arrays
    if in_memory:
        imgs = [reader.data for reader in readers]
        data = np.stack(imgs).squeeze()

    else:
        imgs = [reader.dask_data for reader in readers]
        data = da.stack(imgs).squeeze()

    # Construct empty metadata to pass through
    meta = {}

    # If multiple files were read we need to increment channel axis due to stack
    # But we only do this is the channel axis isn't single to begin with
    img_contains_channels = Dimensions.Channel in readers[0].dims
    if img_contains_channels:
        # Get channel names for display
        channel_names = readers[0].get_channel_names()

        # Only display first channel (protects against image overload)
        visible = [True if i == 0 else False for i, _ in enumerate(channel_names)]

        # Fix channel axis in the case of squeezed or many image stack
        channel_axis = readers[0].dims.index(Dimensions.Channel)
        if readers[0].shape[channel_axis] > 1:
            if len(paths) > 1:
                channel_axis += 1

            # Construct basic metadata
            meta["name"] = channel_names
            meta["channel_axis"] = channel_axis
            meta["visible"] = visible

    return [(data, meta, "image")]


def get_reader(path: PathLike, in_memory: bool) -> Optional[ReaderFunction]:
    """
    Given a single path or list of paths, return the appropriate aicsimageio reader.
    """
    # Standardize path to list of paths
    paths = [path] if isinstance(path, str) else path

    # See if there is a supported reader for the file(s) provided
    try:
        # There is an assumption that the images are stackable and
        # I think it is also safe to assume that if stackable, they are of the same type
        # So only determine reader for the first one
        AICSImage.determine_reader(paths[0])

        # The above line didn't error so we know we have a supported reader
        # Return a partial function with in_memory determined
        return partial(reader_function, in_memory=in_memory)

    # No supported reader, return None
    except exceptions.UnsupportedFileFormatError:
        return None
