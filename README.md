# napari-aicsimageio

[![License](https://img.shields.io/pypi/l/napari-aicsimageio.svg?color=green)](https://github.com/AllenCellModeling/napari-aicsimageio/raw/main/LICENSE)
[![Build Status](https://github.com/AllenCellModeling/napari-aicsimageio/workflows/Build%20Main/badge.svg)](https://github.com/AllenCellModeling/napari-aicsimageio/actions)
[![Code Coverage](https://codecov.io/gh/AllenCellModeling/napari-aicsimageio/branch/main/graph/badge.svg)](https://codecov.io/gh/AllenCellModeling/napari-aicsimageio)

AICSImageIO bindings for napari

---

## Features

-   Supports reading metadata and imaging data for:
    -   `OME-TIFF`
    -   `TIFF`
    -   `CZI`
    -   `LIF`
    -   `ND2`
    -   `DV`
    -   Any formats supported by [aicsimageio](https://github.com/AllenCellModeling/aicsimageio)
    -   Any formats supported by [bioformats](https://github.com/tlambert03/bioformats_jar)
    -   Any additional format supported by [imageio](https://github.com/imageio/imageio)

_While upstream `aicsimageio` is released under BSD-3 license, this plugin is released under GPLv3 license because it installs all format reader dependencies._

## Installation

**Stable Release:** `pip install napari-aicsimageio`<br>
**Development Head:** `pip install git+https://github.com/AllenCellModeling/napari-aicsimageio.git`

### Plugin Variants

![screenshot of plugin sorter showing that napari-aicsimageio-in-memory should be placed above napari-aicsimageio-out-of-memory](https://raw.githubusercontent.com/AllenCellModeling/napari-aicsimageio/main/images/plugin-sorter.png)

There are two variants of this plugin that are added during installation:

-   `aicsimageio-in-memory`, which reads an image fully into memory
-   `aicsimageio-out-of-memory`, which delays reading ZYX chunks until required.
    This allows for incredibly large files to be read and displayed.

## Examples of Features

#### General Image Reading

All image file formats supported by
[aicsimageio](https://github.com/AllenCellModeling/aicsimageio) will be read and all
raw data will be available in the napari viewer.

In addition, when reading an OME-TIFF, you can view all OME metadata directly in the
napari viewer thanks to `ome-types`.

![screenshot of an OME-TIFF image view, multi-channel, z-stack, with metadata viewer](https://raw.githubusercontent.com/AllenCellModeling/napari-aicsimageio/main/images/ome-tiff-with-metadata-viewer.png)

#### Multi-Scene Selection

When reading a multi-scene file, a widget will be added to the napari viewer to manage
scene selection (clearing the viewer each time you change scene or adding the
scene content to the viewer) and a list of all scenes in the file.

![gif of drag and drop file to scene selection and management](https://raw.githubusercontent.com/AllenCellModeling/napari-aicsimageio/main/images/scene-selection.gif)

#### Access to the AICSImage Object and Metadata

![napari viewer with console open showing `viewer.layers[0].metadata`](https://raw.githubusercontent.com/AllenCellModeling/napari-aicsimageio/main/images/console-access.png)

You can access the `AICSImage` object used to load the image pixel data and
image metadata using the built-in napari console:

```python
img = viewer.layers[0].metadata["aicsimage"]
img.dims.order  # TCZYX
img.channel_names  # ["Bright", "Struct", "Nuc", "Memb"]
img.get_image_dask_data("ZYX")  # dask.array.Array
```

The napari layer metadata dictionary also stores a shorthand
for the raw image metadata:

```python
viewer.layers[0].metadata["raw"]
```

The metadata is returned in whichever format is used by the underlying
file format reader, i.e. for CZI the raw metadata is returned as
an `xml.etree.ElementTree.Element`, for OME-TIFF the raw metadata is returned
as an `OME` object from `ome-types`.

Lastly, if the underlying file format reader has an OME metadata conversion function,
you may additionally see a key in the napari layer metadata dictionary
called `"ome_types"`. For example, because the AICSImageIO
`CZIReader` and `BioformatsReader` both support converting raw image metadata
to OME metadata, you will see an `"ome_types"` key that stores the metadata transformed
into the OME metadata model.

```python
viewer.layers[0].metadata["ome_types"]  # OME object from ome-types
```

#### Mosaic Reading

When reading CZI or LIF images, if the image is a mosaic tiled image, `napari-aicsimageio`
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

_Free software: GPLv3_
