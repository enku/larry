# pylint: disable=missing-docstring
from unittest import TestCase, mock

from unittest_fixtures import Fixtures, given

from larry.plugins import GIRepository, gnome_terminal

from . import lib, make_colors


@given(lib.configmaker)
@mock.patch.object(GIRepository, "Gio", create=True)
class PluginTests(TestCase):
    def test(self, gio, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        configmaker.add_section("plugins:gnome_terminal")
        configmaker.add_config(profiles="a b c", color="1d1e28")
        colors = make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )

        gnome_terminal.plugin(colors, configmaker.config["plugins:gnome_terminal"])

        new_with_path_calls = []
        for profile in "abc":
            path = gnome_terminal.get_path(profile)
            new_with_path_calls.append(mock.call(gnome_terminal.SCHEMA, path))
            new_with_path_calls.append(
                new_with_path_calls[-1].set_string("background-color", mock.ANY)
            )
        gio.Settings.new_with_path.assert_has_calls(new_with_path_calls)


class GetPathTests(TestCase):
    def test(self):
        profile = "testtesttest"

        path = gnome_terminal.get_path(profile)

        self.assertEqual(path, "/org/gnome/terminal/legacy/profiles:/:testtesttest/")
