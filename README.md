# napari-aicsimageio

[![Build Status](https://github.com/AllenCellModeling/napari-aicsimageio/workflows/Build%20Master/badge.svg)](https://github.com/AllenCellModeling/napari-aicsimageio/actions)
[![Code Coverage](https://codecov.io/gh/AllenCellModeling/napari-aicsimageio/branch/master/graph/badge.svg)](https://codecov.io/gh/AllenCellModeling/napari-aicsimageio)

AICSImageIO bindings for napari

---

## Features

-   Supports reading metadata and imaging data for:
    -   `OME-TIFF`
    -   `TIFF`
    -   Any formats supported by [aicsimageio](https://github.com/AllenCellModeling/aicsimageio)
        -   `CZI` -- requires additional installation (`pip install aicsimageio[czi]`)
        -   `LIF` -- requires additional installation (`pip install aicsimageio[lif]`)
        -   Any formats supported by
            [imageio](https://github.com/imageio/imageio) (`PNG`, `GIF`, etc.)
            -- requires additional installation (`pip install aicsimageio[base-imageio]`)

## Installation

**Stable Release:** `pip install napari-aicsimageio`<br>
**Development Head:** `pip install git+https://github.com/AllenCellModeling/napari-aicsimageio.git`

See
[aicsimageio Installation documentation](https://github.com/AllenCellModeling/aicsimageio#installation)
for more details on installing support for additional file formats.

### Plugin Variants

![screenshot of plugin sorter showing that napari-aicsimageio-in-memory should be placed above napari-aicsimageio-out-of-memory](https://raw.githubusercontent.com/AllenCellModeling/napari-aicsimageio/main/images/plugin-sorter.png)

There are two variants of this plugin that are added during installation:

-   `aicsimageio-in-memory`, which reads an image fully into memory
-   `aicsimageio-out-of-memory`, which delays reading ZYX chunks until required.
    This allows for incredible large files to be read and displayed.

## Examples of Features

#### General Image Reading

All image file formats supported by
[aicsimageio](https://github.com/AllenCellModeling/aicsimageio) will be read and all
raw data will be available in the napari viewer.

In addition, when reading an OME-TIFF, you can view all OME metadata directly in the
napari viewer thanks to `ome-types`.

![screenshot of an OME-TIFF image view, multi-channel, z-stack, with metadata viewer](https://raw.githubusercontent.com/AllenCellModeling/napari-aicsimageio/main/images/ome-tiff-with-metadata-viewer.png)

#### Mosaic CZI Reading

When reading CZI images, if the image is a mosaic tiled image, `napari-aicsimageio`
will return the reconstructed image:

![screenshot of a reconstructed / restitched mosaic tile CZI](https://raw.githubusercontent.com/AllenCellModeling/napari-aicsimageio/main/images/tiled-czi.png)

#### Mosaic LIF Reading

When reading LIF images, if the image is a mosaic tiled image, `napari-aicsimageio`
will return the reconstructed image:

![screenshot of a reconstructed / restitched mosaic tile LIF](https://raw.githubusercontent.com/AllenCellModeling/napari-aicsimageio/main/images/tiled-lif.png)

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.

For additional file format support, contributed directly to
[AICSImageIO](https://github.com/AllenCellModeling/aicsimageio).
New file format support will become directly available in this
plugin on new `aicsimageio` releases.

## Citation

If you find `aicsimageio` _(or `napari-aicsimageio`)_ useful, please cite as:

> AICSImageIO Contributors (2021). AICSImageIO: Image Reading, Metadata Conversion, and Image Writing for Microscopy Images in Pure Python [Computer software]. GitHub. https://github.com/AllenCellModeling/aicsimageio

_Free software: BSD-3-Clause_
