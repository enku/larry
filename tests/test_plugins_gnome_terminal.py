# pylint: disable=missing-docstring
from unittest import mock

from larry.plugins import gnome_terminal

from . import ConfigTestCase, TestCase, make_colors


@mock.patch("larry.plugins.gnome_terminal.gio")
class PluginTests(ConfigTestCase):
    def test(self, gio):
        self.add_section("plugins:gnome_terminal")
        self.add_config(profiles="a b c", color="1d1e28")
        colors = make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )

        gnome_terminal.plugin(colors, self.config["plugins:gnome_terminal"])

        Gio = gio.return_value  # pylint: disable=invalid-name
        new_with_path_calls = []
        for profile in "abc":
            path = gnome_terminal.get_path(profile)
            new_with_path_calls.append(mock.call(gnome_terminal.SCHEMA, path))
            new_with_path_calls.append(
                new_with_path_calls[-1].set_string("background-color", mock.ANY)
            )
        Gio.Settings.new_with_path.assert_has_calls(new_with_path_calls)


class GetPathTests(TestCase):
    def test(self):
        profile = "testtesttest"

        path = gnome_terminal.get_path(profile)

        self.assertEqual(path, "/org/gnome/terminal/legacy/profiles:/:testtesttest/")
