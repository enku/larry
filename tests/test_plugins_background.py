# pylint: disable=missing-docstring
from configparser import ConfigParser
from unittest import TestCase, mock

from larry.plugins import GIRepository, background

from .lib import make_colors


@mock.patch.object(GIRepository, "Gio", create=True)
class BackgroundTests(TestCase):
    def test(self, gio):
        colors = make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )
        config = ConfigParser()
        config.add_section("plugins:background")
        config.set("plugins:background", "filter", "neonize")

        background.plugin(colors, config["plugins:background"])

        gio.Settings.new.assert_called_once_with(background.SCHEMA)
        settings = gio.Settings.new.return_value
        settings.set_string.assert_has_calls(
            [
                mock.call("primary-color", "#dc00ff"),
                mock.call("secondary-color", "#00f0ff"),
            ]
        )
