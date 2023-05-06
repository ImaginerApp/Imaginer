# main.py
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

import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Gio, Adw, GLib, Pango
from .window import ImaginerWindow

import requests
from os.path import basename, splitext
import io
import threading
import json
from PIL import Image, UnidentifiedImageError
import time

from enum import Enum
import requests
import openai
import re
import unicodedata
from time import gmtime, strftime


class ImaginerApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id="page.codeberg.Imaginer.Imaginer",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.create_action("quit", self.on_quit_action, ["<primary>q"])
        self.create_action("about", self.on_about_action)
        self.create_action("preferences", self.on_preferences_action)
        self.create_action("get_started", self.on_get_started_action)
        self.create_action("imagine", self.on_imagine_action, ["<primary>Return"])
        self.create_action("choose_output", self.on_file_chooser, ["<primary>s"])
        self.create_action("new_window", self.on_new_window_action, ["<primary>n"])

    def on_quit_action(self, action, _):
        """Callback for the app.quit action."""
        self.quit()

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.win = self.props.active_window
        if not self.win:
            self.win = ImaginerWindow(application=self)
        self.win.present()

        self.file_chooser = Gtk.FileChooserNative()
        self.file_chooser.set_title(_("Choose a directory"))
        self.file_chooser.set_transient_for(self.win)
        self.file_chooser.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        self.file_chooser.set_modal(True)
        self.file_chooser.connect("response", self.on_file_chooser_response)
        self.token = ""

    def on_new_window_action(self, action, _):
        """Callback for the app.new_window action."""
        ImaginerWindow(application=self).present()

    def query(self, payload, url):
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
        else:
            headers = {}
        response = requests.post(url, headers=headers, json=payload)
        return response.content

    def on_file_chooser(self, widget, _):
        """Callback for the app.choose_output action."""
        self.file_chooser.show()

    def on_file_chooser_response(self, _, response):
        if response == Gtk.ResponseType.ACCEPT:
            self.directory = self.file_chooser.get_file()
            dir_basename = self.directory.get_basename()
            self.win.label_output.set_label(dir_basename)
            self.win.button_imagine.set_has_tooltip(False)

        self.file_chooser.hide()

        if response == Gtk.ResponseType.ACCEPT:
            self.file_path = self.directory.get_path()

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name="Imaginer",
            application_icon="page.codeberg.Imaginer.Imaginer",
            developer_name="0xMRTT",
            designers=["David Lapshin https://github.com/daudix-UFO"],
            translator_credits="""0xMRTT <0xmrtt@proton.me>
                David Lapshin <ddaudix@gmail.com>""",
            version="0.1.3",
            developers=["0xMRTT https://codeberg.org/0xMRTT"],
            copyright="© 2023 0xMRTT",
        )
        about.add_acknowledgement_section(
            "Special thanks to",
            [
                "Upscaler https://gitlab.com/TheEvilSkeleton/Upscaler",
            ],
        )

        about.present()

    def on_get_started_action(self, widget, _):
        """Callback for the app.get_started action."""
        self.win.stack_imaginer.set_visible_child_name("stack_imagine")

    def slugify(self, value):
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        value = re.sub("[^\w\s-]", "", value).strip().lower()
        return re.sub("[-\s]+", "-", value)

    def on_imagine_action(self, widget, _):
        """Callback for the app.imagine action."""
        self.win.banner.set_revealed(False)
        self.win.stack_imaginer.set_visible_child_name("stack_loading")
        self.win.spinner_loading.start()

        self.provider = self.win.provider.props.selected

        class ProvidersEnum(Enum):
            STABLE_DIFFUSION = 0
            OPENAI = 1
            WAIFU_DIFFUSION = 2
            OPENJOURNEY = 3
            NITRO_DIFFUSION = 4
            ANALOG_DIFFUSION = 5
            PORTRAIT_PLUS = 6

        prompt = self.win.prompt.get_text()
        negative_prompt = self.win.negative_prompt.get_text()
        self.token = self.win.token.get_text()
        openai.api_key = self.token


        def thread_run():
            try:
                path = self.file_path
                print(path)
            except AttributeError:
                path = "imaginer"
            else:
                path = f"{path}/imaginer-{self.slugify(prompt)}-{strftime('%d-%b-%Y-%H-%M-%S', gmtime())}"

            match self.provider:
                case ProvidersEnum.OPENAI.value:
                    try:
                        response = openai.Image.create(
                            prompt=prompt, n=1, size="1024x1024"
                        )
                        image_url = response["data"][0]["url"]
                        image_bytes = requests.get(image_url).content
                    except openai.error.AuthenticationError:
                        self.win.banner.set_title("Invalid API Key")
                        self.win.banner.set_revealed(True)
                        image_bytes = None

                case ProvidersEnum.STABLE_DIFFUSION.value:
                    image_bytes = self.query(
                        {
                            "inputs": prompt,
                            "negative_prompts": negative_prompt if negative_prompt else "",
                        },
                        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
                    )
                    path = f"{path}-stable-diffusion.png"
                case ProvidersEnum.WAIFU_DIFFUSION.value:
                    image_bytes = self.query(
                        {
                            "inputs": prompt,
                            "negative_prompts": negative_prompt if negative_prompt else "",
                        },
                        "https://api-inference.huggingface.co/models/hakurei/waifu-diffusion",
                    )
                    path = f"{path}-waifu-diffusion.png"
                case ProvidersEnum.OPENJOURNEY.value:
                    image_bytes = self.query(
                        {
                            "inputs": prompt,
                            "negative_prompts": negative_prompt if negative_prompt else "",
                        },
                        "https://api-inference.huggingface.co/models/prompthero/openjourney",
                    )
                    path = f"{path}-openjourney.png"
                case ProvidersEnum.NITRO_DIFFUSION.value:
                    image_bytes = self.query(
                        {
                            "inputs": prompt,
                            "negative_prompts": negative_prompt if negative_prompt else "",
                        },
                        "https://api-inference.huggingface.co/models/nitrosocke/Nitro-Diffusion",
                    )
                    path = f"{path}-nitro-diffusion.png"
                case ProvidersEnum.ANALOG_DIFFUSION.value:
                    image_bytes = self.query(
                        {
                            "inputs": prompt,
                            "negative_prompts": negative_prompt if negative_prompt else "",
                        },
                        "https://api-inference.huggingface.co/models/wavymulder/Analog-Diffusion",
                    )
                    path = f"{path}-analog-diffusion.png"
                case ProvidersEnum.PORTRAIT_PLUS.value:
                    image_bytes = self.query(
                        {
                            "inputs": prompt,
                            "negative_prompts": negative_prompt if negative_prompt else "",
                        },
                        "https://api-inference.huggingface.co/models/wavymulder/portraitplus",
                    )
                    path = f"{path}-portrait-plus.png"
            if image_bytes:
                try:
                    image = Image.open(io.BytesIO(image_bytes))
                except UnidentifiedImageError:
                    error = json.loads(image_bytes)["error"]
                    self.win.banner.set_title(error)
                    self.win.banner.set_revealed(True)
                    image = None
            else:
                image = None

            GLib.idle_add(cleanup, image, path)

        def cleanup(image, path):
            self.win.spinner_loading.stop()
            self.win.stack_imaginer.set_visible_child_name("stack_imagine")
            t.join()
            if image:
                image.save(path)
                self.win.image.set_file(Gio.File.new_for_path(path))

        t = threading.Thread(target=thread_run)
        t.start()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print("app.preferences action activated")

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


def main(version):
    """The application's entry point."""
    app = ImaginerApplication()
    return app.run(sys.argv)
