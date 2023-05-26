from .base import ImaginerProvider

import requests
import socket
import json

from gi.repository import Gtk, Adw, GLib

from PIL import Image, UnidentifiedImageError
import io
import base64

class StableDiffusionLocalProvider(ImaginerProvider):
    name = "Local Stable Diffusion"
    slug = "stablediffusionlocal"
    version = "0.1.0"
    url = "https://imaginer.codeberg.page/help/local"
    api_url = ""

    def __init__(self, win, app, *args, **kwargs):
        super().__init__(win, app, *args, **kwargs)

    def ask(self, prompt, negative_prompt):
        if self.api_url:
            try:
                payload = json.dumps(
                        {
                            "prompt": prompt,
                            "negative_prompts": negative_prompt if negative_prompt else "",
                        }
                )
                headers = {"Content-Type": "application/json"}
                url = f"{self.api_url}/sdapi/v1/txt2img"
                response = requests.request("POST", url, headers=headers, data=payload)
                if response.status_code == 403:
                    self.no_api_key()
                    return ""
                elif response.status_code != 200:
                    self.no_api_key(title=response.json()["error"])
                    return ""
                response = response.json()
            except KeyError:
                pass
            except socket.gaierror:
                self.no_connection()
                return ""
            else:
                self.hide_banner()
                if response:
                    try:
                        img = io.BytesIO(base64.b64decode(response["images"][0]))
                        return Image.open(img)
                    except UnidentifiedImageError:
                        error = json.loads(response)["error"]
                        self.no_api_key(title=error)
                        return None
                else:
                    print("No response")
                    return None
        else:
            self.no_api_key(title="No API URL selected, you can choose one in preferences")


    @property
    def require_api_key(self):
        return False

    def preferences(self, win):
        self.pref_win = win

        self.expander = Adw.ExpanderRow()
        self.expander.props.title = self.name

        self.expander.add_action(self.about())  # TODO: in Adw 1.4, use add_suffix
        self.expander.add_action(self.enable_switch())

        self.api_row = Adw.EntryRow()
        self.api_row.connect("apply", self.on_apply)
        self.api_row.props.text = self.api_url
        self.api_row.props.title = "API Url"
        self.api_row.set_show_apply_button(True)
        self.api_row.add_suffix(self.how_to_get_a_token())
        self.expander.add_row(self.api_row)

        return self.expander

    def on_apply(self, widget):
        self.hide_banner()
        self.api_url = self.api_row.get_text()

    def save(self):
        return {"api_url": self.api_url}

    def load(self, data):
        if data["api_url"]:
            self.api_url = data["api_url"]
