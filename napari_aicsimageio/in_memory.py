#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional

from napari.types import PathLike, ReaderFunction
from napari_plugin_engine import napari_hook_implementation

from . import core

###############################################################################


@napari_hook_implementation
def napari_get_reader(path: PathLike) -> Optional[ReaderFunction]:
    return core.get_reader(path, in_memory=True)
