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
    * Any formats supported by [aicsimageio](https://github.com/AllenCellModeling/aicsimageio)
    * Any additional format supported by [imageio](https://github.com/imageio/imageio)

## Installation
**Stable Release:** `pip install napari-aicsimageio`<br>
**Development Head:** `pip install git+https://github.com/AllenCellModeling/napari-aicsimageio.git`

### Plugin Variants

![screenshot of plugin sorter showing that napari-aicsimageio-in-memory should be placed above napari-aicsimageio-out-of-memory](https://github.com/AllenCellModeling/napari-aicsimageio/tree/main/images/plugin-sorter.png)

There are two variants of this plugin that are created during installation:
* `aicsimageio-in-memory`, which reads the image fully into memory
* `aicsimageio-out-of-memory`,
which delays reading ZYX chunks until requested for large file support

## Examples of Features

#### General Image Reading

All image file formats supported by
[aicsimageio](https://github.com/AllenCellModeling/aicsimageio) will be read and all
raw data will be available in the napari viewer.

In addition, when reading an OME-TIFF, you can view all OME metadata directly in the
napari viewer thanks to `ome-types`.

![screenshot of an OME-TIFF image view, multi-channel, z-stack, with metadata viewer](https://github.com/AllenCellModeling/napari-aicsimageio/tree/main/images/ome-tiff-with-metadata-viewer.png)

#### Mosaic CZI Reading

When reading CZI images, if the image is a mosaic tiled image, `napari-aicsimageio`
will return the reconstructed image:

![screenshot of a reconstructed / restitched mosaic tile CZI](https://github.com/AllenCellModeling/napari-aicsimageio/tree/main/images/tiled-czi.png)

#### Mosaic LIF Reading

When reading LIF images, if the image is a mosaic tiled image, `napari-aicsimageio`
will return the reconstructed image:

![screenshot of a reconstructed / restitched mosaic tile LIF](https://github.com/AllenCellModeling/napari-aicsimageio/tree/main/images/tiled-lif.png)

## Development
See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.

For additional file format support, contributed directly to
[AICSImageIO](https://github.com/AllenCellModeling/aicsimageio).
New file format support will become directly available in this
plugin on new `aicsimageio` releases.

***Free software: BSD-3-Clause***
