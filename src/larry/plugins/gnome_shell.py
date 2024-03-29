"""GNOME Shell plugin"""

import configparser
import pathlib
import shutil
import tempfile
import typing as t

from larry import Color, ColorList
from larry.color import COLORS_RE, replace_string, ungray
from larry.config import ConfigType
from larry.plugins import gir

DEFAULT_GRAY_THRESHOLD = 35
THEME_GSETTINGS_NAME = "name"
THEME_GSETTINGS_SCHEMA = "org.gnome.shell.extensions.user-theme"
THEME_INDEX_GNOME_SECTION = "X-GNOME-Metatheme"


class Theme:
    """Represents a theme and it's filesystem structure

    (Right now) it only cares about the GNOME Shell parts
    """

    def __init__(self, name_or_path: str) -> None:
        if "/" in name_or_path:
            self._path = pathlib.Path(name_or_path)
            self._name = self._path.name
        else:
            self._path = pathlib.Path(f"~/.themes/{name_or_path}").expanduser()
            self._name = name_or_path

    @property
    def name(self) -> str:
        """Return the name of the theme

        This is basically the last part of the .path
        """
        return self._name

    @property
    def path(self) -> pathlib.Path:
        """Return the filesystem path of the theme

        This is either the path passed into the intitializer or inferred from the user's
        home directory
        """
        return self._path

    @classmethod
    def current(cls) -> t.Self:
        """Return the user's current system Theme"""
        settings = gir.Gio.Settings(schema=THEME_GSETTINGS_SCHEMA)

        return cls(settings.get_string(THEME_GSETTINGS_NAME))

    def set(self) -> None:
        """Set the theme as the GNOME Shell theme"""
        settings = gir.Gio.Settings(schema=THEME_GSETTINGS_SCHEMA)
        settings.set_string(THEME_GSETTINGS_NAME, self.name)

    def delete(self) -> None:
        """Delete the theme from the filesystem"""
        if type(self).current().path == self.path:
            settings = gir.Gio.Settings(schema=THEME_GSETTINGS_SCHEMA)
            settings.reset(THEME_GSETTINGS_NAME)

        shutil.rmtree(self.path)

    def copy(self) -> t.Self:
        """Create a new theme (dir) using the template gnome-shell directory"""
        template_dir = self._path
        base_dir = pathlib.Path("~/.themes").expanduser()
        theme_path = pathlib.Path(tempfile.mkdtemp(prefix="larry-", dir=base_dir))
        shutil.copytree(template_dir, theme_path, dirs_exist_ok=True)
        new_theme = type(self)(str(theme_path))

        index = configparser.ConfigParser()
        index.read(new_theme.index_path)

        if THEME_INDEX_GNOME_SECTION not in index:
            index.add_section(THEME_INDEX_GNOME_SECTION)

        index.set(THEME_INDEX_GNOME_SECTION, "Name", new_theme.name)
        index.set(THEME_INDEX_GNOME_SECTION, "Comment", "Author: Larry the Cow")

        with new_theme.index_path.open("w", encoding="utf-8") as fp:
            index.write(fp)

        return new_theme

    @classmethod
    def from_template(cls, template: str, colors: ColorList) -> t.Self:
        """Create new gnome-shell theme base on the given template"""
        theme_template = cls(template)
        theme_color = next(Color.generate_from(colors, 1, randomize=False))

        new_theme = theme_template.copy()
        orig_css = theme_template.gnome_shell_css_path.read_text(encoding="utf-8")
        orig_colors = set(Color(s) for s in COLORS_RE.findall(orig_css))

        colormap = {
            color: ungray([color])[0].colorify(theme_color) for color in orig_colors
        }

        new_css = replace_string(orig_css, colormap)
        new_theme.gnome_shell_css_path.write_text(new_css, encoding="utf-8")

        return new_theme

    @property
    def gnome_shell_css_path(self) -> pathlib.Path:
        """Return the path of the theme's gnome-shell.css file"""
        return self.path.joinpath("gnome-shell", "gnome-shell.css")

    @property
    def index_path(self) -> pathlib.Path:
        """Return the path of the theme's index.theme file"""
        return self.path.joinpath("index.theme")


def plugin(colors: ColorList, config: ConfigType) -> None:
    """Plugin runner"""
    current_theme = Theme.current()
    new_theme = Theme.from_template(
        str(pathlib.Path(config["template"]).expanduser()), colors
    )

    new_theme.set()

    if current_theme.name.startswith("larry-"):
        current_theme.delete()
