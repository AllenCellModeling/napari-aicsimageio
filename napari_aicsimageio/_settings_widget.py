import napari
from magicgui import magic_factory

import napari_aicsimageio.core


@magic_factory(
    delimiter={"label": "Delimiter in scene labels:"},
    in_mem_size={"label": "Threshold for \
        <br>out-of-memory loading \
        <br>(GB)"},
    frac_mem_size={
        "label": "Threshold for <br>out-of-memory loading \
            <br>(% free memory):"
    },
    call_button="Apply Reader Settings",
    info_label=dict(
        widget_type="Label",
        label="<h4>For each napari session, \
            <br>to use the settings: \
            <br>press the Apply button!</h4>",
    ),
    persist=True,
)
def set_settings(
    info_label: str,
    delimiter: str = napari_aicsimageio.core.SCENE_LABEL_DELIMITER,
    in_mem_size: float = napari_aicsimageio.core.IN_MEM_THRESHOLD_SIZE_BYTES / 1e9,
    frac_mem_size: int = int(napari_aicsimageio.core.IN_MEM_THRESHOLD_PERCENT * 100),
) -> None:
    
    napari_aicsimageio.core.SCENE_LABEL_DELIMITER = delimiter
    napari_aicsimageio.core.IN_MEM_THRESHOLD_SIZE_BYTES = in_mem_size * 1e9
    napari_aicsimageio.core.IN_MEM_THRESHOLD_PERCENT = frac_mem_size / 100
