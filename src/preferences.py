from gi.repository import Gtk, Adw

from .provider import PROVIDERS


@Gtk.Template(resource_path="/page/codeberg/Imaginer/Imaginer/ui/preferences.ui")
class Preferences(Adw.PreferencesWindow):
    __gtype_name__ = "Preferences"

    provider_group = Gtk.Template.Child()

    def __init__(self, application, **kwargs):
        super().__init__(**kwargs)

        self.app = application
        self.settings = application.settings
        self.setup_providers()

    def setup_providers(self):
        for provider in PROVIDERS.values():
            if provider.slug in self.app.providers:
                self.provider_group.add(
                    self.app.providers[provider.slug].preferences(win=self.app.win)
                )
            else:
                self.provider_group.add(
                    provider(self.app.win, self.app).preferences(win=self.app.win)
                )
            
