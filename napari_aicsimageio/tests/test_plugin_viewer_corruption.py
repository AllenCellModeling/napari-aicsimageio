#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import mock

import napari


def test_viewer_show_only_called_once():
    with mock.patch("napari.gui_qt"):
        with mock.patch("napari.Viewer") as mocked_viewer:
            with napari.gui_qt():
                napari.Viewer()

            mocked_viewer.assert_called_once()
