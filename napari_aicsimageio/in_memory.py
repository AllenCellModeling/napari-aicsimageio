#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional

from pluggy import HookimplMarker

from . import core

###############################################################################

napari_hook_implementation = HookimplMarker("napari")

###############################################################################


@napari_hook_implementation
def napari_get_reader(path: core.PathLike) -> Optional[core.ReaderFunction]:
    return core.get_reader(path, compute=True)
