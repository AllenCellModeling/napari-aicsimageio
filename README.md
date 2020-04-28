# napari-aicsimageio

[![Build Status](https://github.com/AllenCellModeling/napari-aicsimageio/workflows/Build%20Master/badge.svg)](https://github.com/AllenCellModeling/napari-aicsimageio/actions)
[![Code Coverage](https://codecov.io/gh/AllenCellModeling/napari-aicsimageio/branch/master/graph/badge.svg)](https://codecov.io/gh/AllenCellModeling/napari-aicsimageio)

AICSImageIO bindings for napari

---

## Features
* Supports reading metadata and imaging data for:
    * `CZI`
    * `OME-TIFF`
    * `TIFF`
    * Any formats supported by [`aicsimageio`](https://github.com/AllenCellModeling/aicsimageio)
    * Any additional format supported by [`imageio`](https://github.com/imageio/imageio)
* Two variants of the AICSImageIO bindings:
    * `aicsimageio`, which reads the image fully into memory
    * `aicsimageio-delayed`, which delays reading YX planes until requested for large file support

## Installation
**Stable Release:** `pip install napari-aicsimageio`<br>
**Development Head:** `pip install git+https://github.com/AllenCellModeling/napari-aicsimageio.git`

## Development
See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.

***Free software: BSD-3-Clause***
