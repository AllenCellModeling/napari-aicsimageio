import napari
from magicgui import magic_factory

import napari_aicsimageio.core


@magic_factory(
    delimiter={"label": "Delimiter in scene labels:"},
    in_mem_size={"label": "Threshold for out-of-memory loading (GB)"},
    frac_mem_size={"label": "Threshold for out-of-memory loading (% free memory):"},
    call_button="Set Reader Settings and Close Widget",
)
def set_settings(
    napari_viewer: napari.Viewer,
    delimiter: str = napari_aicsimageio.core.SCENE_LABEL_DELIMITER,
    in_mem_size: float = napari_aicsimageio.core.IN_MEM_THRESHOLD_SIZE_BYTES / 1e9,
    frac_mem_size: int = int(napari_aicsimageio.core.IN_MEM_THRESHOLD_PERCENT * 100),
) -> None:

    napari_aicsimageio.core.SCENE_LABEL_DELIMITER = delimiter
    napari_aicsimageio.core.IN_MEM_THRESHOLD_SIZE_BYTES = in_mem_size * 1e9
    napari_aicsimageio.core.IN_MEM_THRESHOLD_PERCENT = frac_mem_size / 100

    viewer = napari_viewer
    viewer.window.remove_dock_widget(set_settings.native)
