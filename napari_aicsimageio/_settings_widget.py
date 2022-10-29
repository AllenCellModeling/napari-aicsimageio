from typing import List

import napari
from magicgui import magic_factory


@magic_factory(
    delimiter={"label": "Delimiter in scene labels:"},
    in_mem_size={"label": "Threshold for out-of-memory loading (GB)"},
    frac_mem_size={"label": "Threshold for out-of-memory loading (% free memory):"},
    call_button="Set Reader Settings",
)
def set_settings(delimiter: str = " :: ", in_mem_size: float = 4, frac_mem_size: int = 30) -> None:
    import napari_aicsimageio.core

    napari_aicsimageio.core.SCENE_LABEL_DELIMITER = delimiter
    napari_aicsimageio.core.IN_MEM_THRESHOLD_SIZE_BYTES = in_mem_size * 1e9
    napari_aicsimageio.core.IN_MEM_THRESHOLD_PERCENT = frac_mem_size / 100
