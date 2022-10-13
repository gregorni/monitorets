# window.py
#
# Copyright 2022 Jordi Chulia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
from gi.repository import Gtk

from .graph_area import GraphArea
from .headerbar_wrapper import HeaderBarWrapper

@Gtk.Template(resource_path='/org/github/jorchube/gpumonitor/gtk/main-window.ui')
class UIMonitorWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    _overlay = Gtk.Template.Child()

    def __init__(self, title, sampler, color=None, **kwargs):
        super().__init__(**kwargs)
        self._sampler = sampler
        self._color = color

        self._drawing_area = self._build_drawing_area()
        self._overlay.set_child(self._drawing_area)

        self._headerbar_wrapper = HeaderBarWrapper(title)
        self._overlay.add_overlay(self._headerbar_wrapper.headerbar)

        self._graph_area = self._build_graph_area()
        self._sampler.install_new_sample_callback(self._graph_area.add_value)

        self.connect("close-request", self._close_request)
        self._install_motion_event_controller()

        self._sampler.start()

    def _build_graph_area(self):
        return GraphArea(self._drawing_area, self._color)

    def _build_drawing_area(self):
        drawing_area = Gtk.DrawingArea()
        drawing_area.set_hexpand(True)
        drawing_area.set_vexpand(True)

        return drawing_area

    def _install_motion_event_controller(self):
        controller = Gtk.EventControllerMotion()
        controller.connect("enter", self._on_mouse_enter)
        controller.connect("leave", self._on_mouse_leave)
        self._headerbar_wrapper.headerbar.add_controller(controller)

    def _on_mouse_enter(self, user_data, x, y):
        self._headerbar_wrapper.set_visible()

    def _on_mouse_leave(self, user_data):
        self._headerbar_wrapper.set_invisible()

    def _close_request(self, user_data):
        self._sampler.stop()