"""GNOME Shell plugin"""

import pathlib
import shutil
import tempfile

from larry import Color, ColorList
from larry.color import COLORS_RE, replace_string, ungray
from larry.config import ConfigType
from larry.io import read_file, write_file

DEFAULT_GRAY_THRESHOLD = 35
THEME_GSETTINGS_NAME = "name"
THEME_GSETTINGS_SCHEMA = "org.gnome.shell.extensions.user-theme"


def get_current_theme() -> str:
    """Return the name of the current gnome-shell theme"""
    from gi.repository import Gio  # pylint: disable=import-outside-toplevel

    settings = Gio.Settings(schema=THEME_GSETTINGS_SCHEMA)
    return settings.get_string(THEME_GSETTINGS_NAME)


def copy_theme(template: str) -> pathlib.Path:
    """Create a new theme (dir) using the template gnome-shell directory"""
    template_dir = pathlib.Path(template).expanduser()
    base_dir = pathlib.Path("~/.themes").expanduser()
    theme_dir = pathlib.Path(tempfile.mkdtemp(prefix="larry-", dir=base_dir))
    shutil.copytree(template_dir, theme_dir / "gnome-shell")

    index = f"""\
[X-GNOME-Metatheme]
Name={theme_dir.name}
Comment=Author: Larry the Cow
Encoding=UTF-8
GtkTheme=Adwaita
IconTheme=Adwaita
CursorTheme=Adwaita
CursorSize=24
"""
    write_file(str(theme_dir / "index.theme"), index.encode())

    return theme_dir


def create_new_theme(template: str, colors: ColorList, _config: ConfigType) -> str:
    """Create new gnome-shell theme base on the given template"""
    theme_color = next(Color.generate_from(colors, 1, randomize=False))
    theme_dir = copy_theme(template)
    template_dir = pathlib.Path(template).expanduser()
    orig_css = read_file(str(template_dir / "gnome-shell.css")).decode()
    orig_colors = set(Color(s) for s in COLORS_RE.findall(orig_css))

    colormap = {
        color: ungray([color])[0].colorify(theme_color) for color in orig_colors
    }
    new_css = replace_string(orig_css, colormap)

    write_file(str(theme_dir / "gnome-shell" / "gnome-shell.css"), new_css.encode())

    return theme_dir.name


def set_theme(name: str) -> None:
    """Sets the GNOME Shell theme to the given theme"""
    from gi.repository import Gio  # pylint: disable=import-outside-toplevel

    settings = Gio.Settings(schema=THEME_GSETTINGS_SCHEMA)
    settings.set_string(THEME_GSETTINGS_NAME, name)


def delete_theme(name: str) -> None:
    """Delete the given theme dir from ~/.themes"""
    theme_dir = pathlib.Path(f"~/.themes/{name}").expanduser()

    if theme_dir.is_dir():
        shutil.rmtree(theme_dir)


def plugin(colors: ColorList, config: ConfigType) -> None:
    """Plugin runner"""
    current_theme = get_current_theme()
    template = config["template"]
    new_theme = create_new_theme(template, colors, config)

    set_theme(new_theme)

    if current_theme.startswith("larry-"):
        delete_theme(current_theme)
