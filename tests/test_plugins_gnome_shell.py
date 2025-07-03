# pylint: disable=missing-docstring,unused-argument
import os
import os.path
import random
from pathlib import Path
from unittest import TestCase, mock

from unittest_fixtures import Fixtures, given

from larry.color import COLORS_RE, Color
from larry.plugins import GIRepository, gnome_shell

from . import CSS
from . import fixtures as tf
from . import make_colors


@given(tf.tmpdir)
class ThemeTests(TestCase):
    def test_init_with_name(self, fixtures: Fixtures) -> None:
        name = "testtheme"

        theme = gnome_shell.Theme(name)

        self.assertEqual(theme.name, "testtheme")
        self.assertEqual(theme.path, Path("~/.themes/testtheme").expanduser())

    def test_init_with_path(self, fixtures: Fixtures) -> None:
        path = "/path/to/testtheme"

        theme = gnome_shell.Theme(path)

        self.assertEqual(theme.name, "testtheme")
        self.assertEqual(theme.path, Path("/path/to/testtheme").expanduser())

    @mock.patch.object(GIRepository, "Gio", create=True)
    def test_current(self, gio, fixtures: Fixtures) -> None:
        gio.Settings.return_value.get_string.return_value = "test"

        theme = gnome_shell.Theme.current()

        self.assertEqual(theme.name, "test")

    def test_copy(self, fixtures: Fixtures) -> None:
        theme_path = f"{fixtures.tmpdir}/.themes/testtheme"
        os.makedirs(theme_path)
        theme = gnome_shell.Theme(theme_path)
        expanduser = mock_expanduser(fixtures.tmpdir)

        with mock.patch.object(os.path, "expanduser", side_effect=expanduser):
            copy = theme.copy()

        self.assertTrue(copy.path.exists())
        self.assertTrue((copy.path / "index.theme").exists())

    @mock.patch("larry.color.random", random.Random(1))
    def test_from_template(self, fixtures: Fixtures) -> None:
        template_path = f"{fixtures.tmpdir}/.themes/template"
        os.makedirs(template_path)
        create_theme(Path(template_path, "gnome-shell"))
        colors = make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )
        expanduser = mock_expanduser(fixtures.tmpdir)

        with mock.patch.object(os.path, "expanduser", side_effect=expanduser):
            theme = gnome_shell.Theme.from_template(template_path, colors)

        self.assertTrue(theme.path.exists())

        css = theme.gnome_shell_css_path.read_text(encoding="utf-8")
        theme_colors = [Color(s) for s in COLORS_RE.findall(css)]

        expected = make_colors(
            "#4a3441 #33242d #943972 #6c0044 #943972 #6c0044 #33242d"
        )
        self.assertEqual(theme_colors, expected)

    @mock.patch.object(GIRepository, "Gio", create=True)
    def test_set(self, gio, fixtures: Fixtures) -> None:
        theme_path = f"{fixtures.tmpdir}/.themes/testtheme"
        os.makedirs(theme_path)
        theme = gnome_shell.Theme(theme_path)
        expanduser = mock_expanduser(fixtures.tmpdir)

        with mock.patch.object(os.path, "expanduser", side_effect=expanduser):
            theme.set()

        gio.Settings.assert_called_once_with(schema=gnome_shell.THEME_GSETTINGS_SCHEMA)
        settings = gio.Settings.return_value
        settings.set_string.assert_called_once_with("name", "testtheme")

    @mock.patch.object(GIRepository, "Gio", create=True)
    def test_delete(self, gio, fixtures: Fixtures) -> None:
        """Delete itself from the filesystem"""
        theme_path = f"{fixtures.tmpdir}/.themes/testtheme"
        os.makedirs(theme_path)
        theme = gnome_shell.Theme(theme_path)

        self.assertTrue(theme.path.exists())

        theme.delete()

        self.assertFalse(theme.path.exists())
        gio.Settings.return_value.reset.assert_not_called()

    @mock.patch.object(GIRepository, "Gio", create=True)
    def test_delete_when_current_theme(self, gio, fixtures: Fixtures) -> None:
        theme_path = f"{fixtures.tmpdir}/.themes/testtheme"
        os.makedirs(theme_path)
        theme = gnome_shell.Theme(theme_path)
        gio.Settings.return_value.get_string.return_value = theme.name

        self.assertTrue(theme.path.exists())

        expanduser = mock_expanduser(fixtures.tmpdir)
        with mock.patch.object(os.path, "expanduser", side_effect=expanduser):
            theme.delete()

        self.assertFalse(theme.path.exists())
        gio.Settings.return_value.reset.assert_called_once_with("name")


@given(tf.configmaker)
@mock.patch("larry.plugins.gnome_shell.Theme", autospec=True)
class PluginTests(TestCase):
    def test(self, theme_cls, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        configmaker.add_section("plugins:gnome_shell")
        configmaker.add_config(template="test-template")
        colors = make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )
        gnome_shell_config = configmaker.config["plugins:gnome_shell"]

        current_theme = mock.Mock()
        current_theme.name = "larry-test"
        theme_cls.current.return_value = current_theme
        gnome_shell.plugin(colors, gnome_shell_config)

        theme_cls.current.assert_called_once_with()
        theme_cls.from_template.assert_called_once_with("test-template", colors)
        theme = theme_cls.from_template.return_value
        theme.set.assert_called_once_with()
        current_theme.delete.assert_called_once_with()

    def test_when_current_theme_is_not_a_larry_theme(
        self, theme_cls, fixtures: Fixtures
    ) -> None:
        configmaker = fixtures.configmaker
        configmaker.add_section("plugins:gnome_shell")
        configmaker.add_config(template="test-template")
        colors = make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )
        gnome_shell_config = configmaker.config["plugins:gnome_shell"]

        current_theme = mock.Mock()
        current_theme.name = "Adwaita"
        theme_cls.current.return_value = current_theme
        gnome_shell.plugin(colors, gnome_shell_config)

        current_theme.delete.assert_not_called()


def create_theme(theme_dir):
    css_path = theme_dir / "gnome-shell.css"
    css_path.parent.mkdir(parents=True)
    css_path.write_text(CSS, encoding="UTF-8")


def mock_expanduser(home: str):
    def expanduser(path: str):
        parts = [p for p in os.path.split(path) if p]
        if parts[0] == "~":
            return os.path.join(home, *parts[1:])
        return path

    return expanduser
