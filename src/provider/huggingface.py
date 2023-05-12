import requests
import json
from .base import ImaginerProvider

import socket

from gi.repository import Gtk, Adw, GLib
from PIL import Image, UnidentifiedImageError
import io

class BaseHFProvider(ImaginerProvider):
    name = None
    slug = None
    model = None
    url = "https://imaginer.codeberg.page/help/huggingface"

    def __init__(self, win, app, *args, **kwargs):
        super().__init__(win, app, *args, **kwargs)
        self.api_key = None

    def ask(self, prompt, negative_prompt):
        try:
            payload = json.dumps(
                {
                    "inputs": prompt,
                    "negative_prompts": negative_prompt if negative_prompt else "",
                }
            )
            headers = {"Content-Type": "application/json"}
            if self.require_api_key and self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            url = f"https://api-inference.huggingface.co/models/{self.model}"
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 403:
                self.no_api_key()
                return ""
            elif response.status_code != 200:
                self.win.banner.props.title = response.json()["error"]
                self.win.banner.props.button_label = ""
                self.win.banner.set_revealed(True)
                return ""
            response = response.content
        except KeyError:
            print("KeyError")
            pass
        except socket.gaierror:
            self.no_connection()
            return ""
        else:
            self.hide_banner()
            if response:
                try:
                    return Image.open(io.BytesIO(response))
                except UnidentifiedImageError:
                    error = json.loads(response)["error"]
                    self.win.banner.set_title(error)
                    self.win.banner.set_revealed(True)
                    return None
            else:
                print("No response")
                return None

    @property
    def require_api_key(self):
        return True

    def preferences(self, win):
        if self.require_api_key:
            self.expander = Adw.ExpanderRow()
            self.expander.props.title = self.name

            self.expander.add_action(self.about())
            self.expander.add_action(self.enable_switch())

            self.api_row = Adw.PasswordEntryRow()
            self.api_row.connect("apply", self.on_apply)
            self.api_row.props.title = "API Key"
            self.api_row.props.text = self.api_key or ""
            self.api_row.add_suffix(self.how_to_get_a_token())
            self.api_row.set_show_apply_button(True)
            self.expander.add_row(self.api_row)

            return self.expander
        else:
            return self.no_preferences(win)

    def on_apply(self, widget):
        self.hide_banner()
        self.api_key = self.api_row.get_text()
        print(self.api_key)

    def save(self):
        if self.require_api_key:
            return {"api_key": self.api_key}
        return {}

    def load(self, data):
        if self.require_api_key:
            self.api_key = data["api_key"]
