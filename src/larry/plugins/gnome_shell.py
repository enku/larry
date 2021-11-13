"""GNOME Shell plugin"""
import pathlib
import shutil
import tempfile

from larry import Color, ColorList, ConfigType
from larry.color import replace_string
from larry.io import read_file, write_file

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
[Desktop Entry]
Type=X-GNOME-Metatheme
Name={theme_dir.name}
Comment=Author: Larry the Cow
Version=v1.0
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=Adwaita
"""
    write_file(str(theme_dir / "index.theme"), index.encode())

    return theme_dir


def create_new_theme(template: str, colors: ColorList, config: ConfigType) -> str:
    """Create new gnome-shell theme base on the given template"""
    theme_dir = copy_theme(template)
    template_dir = pathlib.Path(template).expanduser()

    theme_color = next(Color.generate_from(colors, 1, randomize=False))
    config_colors = config.get("colors", "").split()
    orig_css = read_file(str(template_dir / "gnome-shell.css")).decode()

    new_css = orig_css

    for color in config_colors:
        new_css = replace_string(new_css, color, theme_color)

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
