# window.py
#
# SPDX-FileCopyrightText: 2023 0xMRTT
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


@Gtk.Template(resource_path="/io/github/ImaginerApp/Imaginer/window.ui")
class ImaginerWindow(Adw.ApplicationWindow):
    __gtype_name__ = "ImaginerWindow"

    toast = Gtk.Template.Child()
    stack_imaginer = Gtk.Template.Child()
    spinner_loading = Gtk.Template.Child()
    image = Gtk.Template.Child()
    button_output = Gtk.Template.Child()
    button_imagine = Gtk.Template.Child()
    label_output = Gtk.Template.Child()
    banner = Gtk.Template.Child()
    prompt = Gtk.Template.Child()
    token = Gtk.Template.Child()
    provider = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
