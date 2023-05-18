# main.py
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

import sys
import gi
import sys
import threading
import json

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")
gi.require_version("Gst", "1.0")
gi.require_version('WebKit', '6.0')

from gi.repository import Gtk, Gio, Adw, Gdk, GLib
from .window import ImaginerWindow
from .preferences import Preferences
from enum import auto, IntEnum

from gettext import gettext as _
from .constants import app_id, version, build_type

from tempfile import NamedTemporaryFile

import unicodedata
from time import gmtime, strftime
from os.path import basename, splitext

from .provider import PROVIDERS
import platform
import os
import tempfile
import re

class KillableThread(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False
    
    def start(self):
        self.__run_backup = self.run
        self.run = self.__run     
        threading.Thread.start(self)
    
    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup
    
    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None
    
    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace
    
    def kill(self):
        self.killed = True

 



class ImaginerApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id="page.codeberg.Imaginer.Imaginer",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.create_action("quit", self.on_quit, ["<primary>q"])
        self.create_action("about", self.on_about_action)
        self.create_action(
            "preferences", self.on_preferences_action, ["<primary>comma"]
        )
        self.create_action("ask", self.on_ask_action, ["<primary>Return"])
        self.create_action("stop", self.on_stop_action, ["<primary>Escape"])
        self.create_action("choose_output", self.on_file_chooser, ["<primary>s"])
        self.create_action("new", self.on_new_window, ["<primary>n"])
        
        # self.create_action("speak", self.on_speak_action, ["<primary>S"])
        # self.create_action("listen", self.on_listen_action, ["<primary>L"])

        self.settings = Gio.Settings(schema_id="page.codeberg.Imaginer.Imaginer")

        self.enabled_providers = sorted(
            set(self.settings.get_strv("enabled-providers"))
        )
        self.latest_provider = self.settings.get_string("latest-provider")

        self.create_stateful_action(
            "set_provider",
            GLib.VariantType.new("s"),
            GLib.Variant("s", self.latest_provider),
            self.on_set_provider_action
        )


    def quitting(self, *args, **kwargs):
        """Called before closing main window."""
        self.settings.set_strv("enabled-providers", list(self.enabled_providers))
        self.settings.set_string("latest-provider", self.provider)

        print("Saving providers data...")

        self.save_providers()
        self.win.close()

    @property
    def win(self):
        return self.props.active_window

    def on_quit(self, action, param):
        """Called when the user activates the Quit action."""
        self.quitting()

    def save_providers(self):
        r = {}
        for k, p in self.providers.items():
            r[p.slug] = json.dumps(p.save())
        data = GLib.Variant("a{ss}", r)
        self.settings.set_value("providers-data", data)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.new_window()

    def on_set_provider_action(self, action, *args):
        self.provider = args[0].get_string()
        Gio.SimpleAction.set_state(self.lookup_action("set_provider"), args[0])

    def on_new_window(self, action, *args):
        self.new_window()

    def new_window(self, window=None):
        if window:
            win = self.props.active_window
        else:
            win = ImaginerWindow(application=self)
        win.connect("close-request", self.quitting)
        self.load_dropdown(win)
        self.load()
        win.file_chooser = Gtk.FileChooserNative()
        win.file_chooser.set_title(_("Choose a directory"))
        win.file_chooser.set_transient_for(win)
        win.file_chooser.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        win.file_chooser.set_modal(True)
        win.file_chooser.connect("response", self.on_file_chooser_response)

        for k, p in self.providers.items():
            if p.slug == self.latest_provider:
                self.provider = k
                break
        win.present()

    def load_dropdown(self, window=None):
        if window is None:
            window = self.win
        self.menu_model = Gio.Menu()
        self.menu_model.append_item(Gio.MenuItem.new(label=_("New Window"), detailed_action="app.new"))

        section_menu = Gio.Menu()

        provider_menu = Gio.Menu()


        self.providers = {}
        self.providers_data = self.settings.get_value("providers-data")

        for provider in self.enabled_providers:
            try:
                item = PROVIDERS[provider]
                item_model = Gio.MenuItem()
                item_model.set_label(item.name)
                item_model.set_action_and_target_value(
                    "app.set_provider",
                    GLib.Variant("s", item.slug))
                provider_menu.append_item(item_model)
            except KeyError:
                print("Provider", provider, "not found")
                continue
            else:
                try:
                    self.providers[item.slug]  # doesn't re load if already loaded
                except KeyError:
                    self.providers[item.slug] = PROVIDERS[provider](window, self)

        section_menu.append_submenu(_("Providers"), provider_menu)

        section_menu.append_item(Gio.MenuItem.new(label=_("Preferences"), detailed_action="app.preferences"))
        section_menu.append_item(Gio.MenuItem.new(label=_("Keyboard Shortcuts"), detailed_action="win.show-help-overlay"))
        section_menu.append_item(Gio.MenuItem.new(label=_("About"), detailed_action="app.about"))

        self.menu_model.append_section(None, section_menu)

        window.menu.set_menu_model(self.menu_model)

    def load(self):
        for p in self.providers.values():
            try:
                p.load(data=json.loads(self.providers_data[p.slug]))
            except KeyError:  # provider not in data
                pass

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name="Imaginer",
            application_icon=app_id,
            developer_name="0xMRTT",
            developers=["0xMRTT https://github.com/0xMRTT"],
            designers=["David Lapshin https://github.com/daudix-UFO"],
            artists=["David Lapshin https://github.com/daudix-UFO"],
            documenters=[],
            translator_credits="""0xMRTT <0xmrtt@proton.me>
                David Lapshin <ddaudix@gmail.com>
                Morgan Antonsson <morgan.antonsson@gmail.com>
                thepoladov13 <thepoladov@protonmail.com>
                Muznyo <codeberg.vqtek@simplelogin.com>
                Deimidis <gmovia@pm.me>
                sjdonado <jsrd98@gmail.com>
                artnay <jiri.gronroos@iki.fi>
                Rene Coty <irenee.thirion@e.email>
                galegovski <galegovski@outlook.com>""",
            license_type=Gtk.License.GPL_3_0,
            version=version,
            website="https://imaginer.codeberg.page",
            issue_url="https://github.com/Imaginer/Imaginer/issues",
            support_url="https://codeberg.org/Imaginer/Imaginer/issues",
            copyright="© 2023 0xMRTT",
        )

        about.add_acknowledgement_section(
            "Special thanks to",
            [
                "Telegraph https://apps.gnome.org/app/io.github.fkinoshita.Telegraph",
                "Apostrophe https://apps.gnome.org/app/org.gnome.gitlab.somas.Apostrophe",
            ],
        )
        about.set_debug_info(
            f"""{app_id} {version}
Environment: {os.environ.get("XDG_CURRENT_DESKTOP", "Unknown")}
Gtk: {Gtk.MAJOR_VERSION}.{Gtk.MINOR_VERSION}.{Gtk.MICRO_VERSION}
Python: {platform.python_version()}
OS: {platform.system()} {platform.release()} {platform.version()}
Providers: {self.enabled_providers}
"""
        )
        about.present()

    def on_preferences_action(self, widget, *args, **kwargs):
        """Callback for the app.preferences action."""
        preferences = Preferences(
            application=self, transient_for=self.props.active_window
        )
        preferences.present()

    def on_file_chooser(self, widget, _):
        """Callback for the app.choose_output action."""
        self.win.file_chooser.show()

    def on_file_chooser_response(self, _, response):
        if response == Gtk.ResponseType.ACCEPT:
            self.directory = self.win.file_chooser.get_file()
            dir_basename = self.directory.get_basename()
            self.win.label_output.set_label(dir_basename)
            self.win.button_imagine.set_has_tooltip(False)

        self.win.file_chooser.hide()

        if response == Gtk.ResponseType.ACCEPT:
            self.file_path = self.directory.get_path()

    def slugify(self, value):
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        value = re.sub("[^\w\s-]", "", value).strip().lower()
        return re.sub("[-\s]+", "-", value)

    def on_ask_action(self, widget, _):
        """Callback for the app.ask action."""


        self.prompt = self.win.prompt.get_text()
        self.negative_prompt = self.win.negative_prompt.get_text()

        try:
            self.path = self.file_path
        except AttributeError:
            self.path = "imaginer"
        else:
            self.path = f"{self.path}/imaginer-{self.slugify(self.prompt)}-{strftime('%d-%b-%Y-%H-%M-%S', gmtime())}"

        if self.prompt == "" or self.prompt is None:  # empty prompt
            return
        else:
            self.win.spinner.start()
            self.win.stack_imaginer.set_visible_child_name("stack_loading")

            def thread_run():
                try:
                    image = self.providers[self.provider].ask(self.prompt, self.negative_prompt)
                except GLib.Error as e:
                    self.win.banner.set_title(str(e))
                    self.win.banner.set_revealed(True)
                else:
                    path = self.providers[self.provider].path(self.path)
                    GLib.idle_add(cleanup, image, path)

            def cleanup(image, path):
                self.win.spinner.stop()
                self.win.stack_imaginer.set_visible_child_name("stack_imagine")
                self.t.join()

                if image:
                    self.win.banner.set_revealed(False)
                    image.save(path)
                    self.win.image.set_file(Gio.File.new_for_path(path))
                    self.win.image.set_visible(True)
                    print("Image saved")
                else:
                    print("No image returned")

            
            self.t = KillableThread(target=thread_run)
            self.t.start()

    def on_stop_action(self, widget, _):
        """Callback for the app.stop action."""
        self.win.spinner.stop()
        self.win.stack_imaginer.set_visible_child_name("stack_imagine")
        self.t.kill()
        self.t.join()

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)
        
    def create_stateful_action(self, name, parameter_type, initial_state, callback, shortcuts=None):
        """Add a stateful application action."""

        action = Gio.SimpleAction.new_stateful(
            name, parameter_type, initial_state)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.parent.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = ImaginerApplication()
    return app.run(sys.argv)
