# pylint: disable=missing-docstring
import os.path
import random
from pathlib import Path
from unittest import mock

from larry.color import COLORS_RE, Color
from larry.plugins import GIRepository, gnome_shell

from . import CSS, TestCase, make_colors


@mock.patch.object(GIRepository, "Gio", create=True)
class GetCurrentThemeTests(TestCase):
    def test(self, gio):
        settings = gio.Settings.return_value
        settings.get_string.return_value = "test"

        self.assertEqual(gnome_shell.get_current_theme(), "test")
        gio.Settings.assert_called_once_with(schema=gnome_shell.THEME_GSETTINGS_SCHEMA)
        settings.get_string.assert_called_once_with(gnome_shell.THEME_GSETTINGS_NAME)


class CreateNewThemeTests(TestCase):
    @mock.patch("larry.color.random", random.Random(1))
    def test(self):
        home_dir = Path(self.tmpdir)
        home_dir.joinpath(".themes").mkdir()
        template_dir = home_dir / "template"
        create_theme(template_dir)
        colors = make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )
        expanduser = mock_expanduser(self.tmpdir)

        with mock.patch.object(os.path, "expanduser", side_effect=expanduser):
            theme_name = gnome_shell.create_new_theme(str(template_dir), colors, None)

        new_theme = home_dir / ".themes" / theme_name
        self.assertTrue((new_theme).exists())
        new_css = (new_theme / "gnome-shell/gnome-shell.css").read_text(
            encoding="UTF-8"
        )
        new_theme_colors = [Color(s) for s in COLORS_RE.findall(new_css)]
        expected = make_colors(
            "#4a3441 #33242d #943972 #6c0044 #943972 #6c0044 #33242d"
        )
        self.assertEqual(new_theme_colors, expected)


@mock.patch.object(GIRepository, "Gio", create=True)
class SetThemeTests(TestCase):
    def test(self, gio):
        gnome_shell.set_theme("test")

        gio.Settings.assert_called_once_with(schema=gnome_shell.THEME_GSETTINGS_SCHEMA)
        settings = gio.Settings.return_value
        settings.set_string.assert_called_once_with("name", "test")


class DeleteThemeTests(TestCase):
    def test(self):
        fake_theme_dir = Path(f"{self.tmpdir}") / "fake_theme"
        fake_theme_dir.mkdir()

        with mock.patch(
            "larry.plugins.gnome_shell.pathlib.Path.expanduser"
        ) as expanduser:
            expanduser.return_value = fake_theme_dir
            gnome_shell.delete_theme("fake_theme")

        self.assertFalse(fake_theme_dir.exists())


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
