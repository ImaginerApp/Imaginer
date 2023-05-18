from .huggingface import BaseHFProvider

from gi.repository import Gtk, Adw, GLib

class CustomProvider(BaseHFProvider):
    name = "Custom Provider"
    slug = "custom"
    url = "https://imaginer.codeberg.page/help/custom"

    def preferences(self, win):
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

        self.model_row = Adw.EntryRow()
        self.model_row.connect("apply", self.on_apply)
        self.model_row.props.title = "Model"
        if self.model:
            self.model_row.props.text = str(self.model)
        else:
            print("No model")
            self.model_row.props.text = ""
        self.model_row.add_suffix(self.how_to_choose_model())
        self.model_row.set_show_apply_button(True)
        self.expander.add_row(self.model_row)
        return self.expander

    def on_apply(self, widget):
        self.hide_banner()
        self.api_key = self.api_row.get_text()
        self.model = str(self.model_row.get_text())
        self.name = self.model.split("/")[-1]
        self.app.save_providers()

    def how_to_choose_model(self):
        about_button = Gtk.Button()
        about_button.set_icon_name("dialog-information-symbolic")
        about_button.set_tooltip_text("How to choose a model")
        about_button.add_css_class("flat")
        about_button.set_valign(Gtk.Align.CENTER)
        about_button.connect("clicked", self.open_documentation)
        return about_button
        
    def save(self):
        return {
            "api_key": self.api_key,
            "model": self.model
        }

    def load(self, data):
        try:
            if data["api_key"]:
                self.api_key = data.get("api_key", "")
            if data["model"]:
                self.model = data.get("model", "")
        except KeyError:
            pass