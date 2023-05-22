# window.py
#
# Copyright 2023 Me
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
from gi.repository import Gtk, Gio


@Gtk.Template(resource_path="/page/codeberg/Imaginer/Imaginer/ui/window.ui")
class ImaginerWindow(Adw.ApplicationWindow):
    __gtype_name__ = "ImaginerWindow"

    toast_overlay = Gtk.Template.Child()
    banner = Gtk.Template.Child()
    stack_imaginer = Gtk.Template.Child()
    image = Gtk.Template.Child()
    button_output = Gtk.Template.Child()
    button_imagine = Gtk.Template.Child()
    spinner = Gtk.Template.Child()
    prompt = Gtk.Template.Child()
    negative_prompt = Gtk.Template.Child()
    menu = Gtk.Template.Child()
    label_output = Gtk.Template.Child()
    image_width_spinbutton = Gtk.Template.Child()
    image_height_spinbutton = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app = kwargs.get('application')
        if app is None:
            raise ValueError("Application should be passed to ImaginerWindow")
        self.app = app

        self.settings = Gio.Settings(schema_id="page.codeberg.Imaginer.Imaginer")

        self.settings.bind(
            "width", self, "default-width", Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "height", self, "default-height", Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "is-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "is-fullscreen", self, "fullscreened", Gio.SettingsBindFlags.DEFAULT
        )

    @Gtk.Template.Callback()
    def on_image_width_changed(self, widget):
        self.app.width = self.image_width_spinbutton.get_value_as_int()
        

    @Gtk.Template.Callback()
    def on_image_height_changed(self, widget):
        self.app.height = self.image_height_spinbutton.get_value_as_int()
