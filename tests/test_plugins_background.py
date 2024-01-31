# pylint: disable=missing-docstring
from unittest import mock

from larry.plugins import background

from . import ConfigTestCase, make_colors


@mock.patch("larry.plugins.background.gir")
class BackgroundTests(ConfigTestCase):
    def test(self, gir):
        colors = make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )

        background.plugin(colors, None)

        gi_repo = gir.return_value
        gi_repo.Gio.Settings.new.assert_called_once_with(background.SCHEMA)
        settings = gi_repo.Gio.Settings.new.return_value
        settings.set_string.assert_has_calls(
            [
                mock.call("primary-color", "#7e118f"),
                mock.call("secondary-color", "#35dfe9"),
            ]
        )
