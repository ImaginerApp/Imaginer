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
        # for provider in self.app.providers.values():
        #     try:
        #         self.provider_group.add(provider.preferences(self))
        #     except TypeError:  # no prefs
        #         pass
        # else:
        #     row = Adw.ActionRow()
        #     row.props.title = "No providers available"
        #     self.provider_group.add(row)
        for provider in PROVIDERS.values():
            try:
                self.provider_group.add(
                    provider(self.app.win, self.app).preferences(self)
                )
            except TypeError:
                pass
