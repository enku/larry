"""GNOME Shell plugin"""
import os
from time import sleep

import dbus

from larry import ConfigType, rgb, rgba, rrggbb
from larry.io import write_file
from larry.types import ColorList


def plugin(colors: ColorList, config: ConfigType) -> None:
    """gnome_shell plugin for larry"""
    theme_color = colors[0]
    template = os.path.expanduser(config["template"])
    outfile = os.path.expanduser(config["location"])
    config_colors = config.get("colors", "").split()

    with open(template) as myfile:
        orig_css = myfile.read()

    new_css = orig_css

    for color in config_colors:
        num_commas = color.count(",")

        if num_commas == 0:
            # rrggbb
            new_css = rrggbb(color, theme_color, new_css)
        elif num_commas == 2:
            # r,g,b
            new_css = rgb(color, theme_color, new_css)
        elif num_commas == 3:
            # r,g,b,a
            new_css = rgba(color, theme_color, new_css)

    write_file(outfile, new_css.encode())

    # tell gnome shell to reload the theme
    gnome_shell_reload_theme()

# Has this plugin been run before?
plugin.has_run = False


def gnome_shell_reload_theme() -> None:
    """Tell gnome shell to reload the theme"""
    if not plugin.has_run:
        # If larry is in your autostart, gnome-shell might not be
        # initialized all the way before this function is called.
        # Calling it too soon causes the original theme to not always
        # get loaded properly. We give it some time.
        sleep(10)
        plugin.has_run = True

    bus = dbus.SessionBus()
    obj = bus.get_object("org.gnome.Shell", "/org/gnome/Shell")
    obj_iface = dbus.Interface(obj, "org.gnome.Shell")
    obj_iface.Eval("Main.loadTheme();")
