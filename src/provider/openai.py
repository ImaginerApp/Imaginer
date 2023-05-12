from .base import ImaginerProvider

import openai
import socket

from gi.repository import Gtk, Adw, GLib

from PIL import Image, UnidentifiedImageError
import io

class OpenAIProvider(ImaginerProvider):
    name = "Open AI"
    slug = "openai"
    version = "0.1.0"
    api_key_title = "API Key"
    url = "https://imaginer.codeberg.page/help/openai"

    def __init__(self, win, app, *args, **kwargs):
        super().__init__(win, app, *args, **kwargs)
        self.chat = openai.ChatCompletion

    def ask(self, prompt, negative_prompt):
        try:
            print("Prompt:", prompt)
            response = openai.Image.create(
                prompt=prompt, n=1, size="1024x1024"
            )
            image_url = response["data"][0]["url"]
            image_bytes = requests.get(image_url).content
        except openai.error.AuthenticationError:
            print("No API key")
            self.no_api_key()
            return ""
        except openai.error.OpenAIError as e:
            print("Invalid request")
            self.win.banner.props.title = e.error["message"]
            self.win.banner.props.button_label = ""
            self.win.banner.set_revealed(True)
            return ""
        except openai.error.RateLimitError:
            print("Rate limit")
            self.win.banner.props.title = "You exceeded your current quota, please check your plan and billing details."
            self.win.banner.props.button_label = ""
            self.win.banner.set_revealed(True)
            return ""
        except socket.gaierror:
            self.no_connection()
            return ""
        else:
            self.hide_banner()
            if image_bytes:
                try:
                    return Image.open(io.BytesIO(image_bytes))
                except UnidentifiedImageError:
                    error = json.loads(image_bytes)["error"]
                    self.win.banner.set_title(error)
                    self.win.banner.set_revealed(True)
                    return None
            else:
                return None


    @property
    def require_api_key(self):
        return True

    def preferences(self, win):
        self.pref_win = win

        self.expander = Adw.ExpanderRow()
        self.expander.props.title = self.name

        self.expander.add_action(self.about())  # TODO: in Adw 1.4, use add_suffix
        self.expander.add_action(self.enable_switch())

        self.api_row = Adw.PasswordEntryRow()
        self.api_row.connect("apply", self.on_apply)
        self.api_row.props.text = openai.api_key or ""
        self.api_row.props.title = self.api_key_title
        self.api_row.set_show_apply_button(True)
        self.api_row.add_suffix(self.how_to_get_a_token())
        self.expander.add_row(self.api_row)

        return self.expander

    def on_apply(self, widget):
        self.hide_banner()
        api_key = self.api_row.get_text()
        openai.api_key = api_key

    def save(self):
        return {"api_key": openai.api_key}

    def load(self, data):
        if data["api_key"]:
            openai.api_key = data["api_key"]
