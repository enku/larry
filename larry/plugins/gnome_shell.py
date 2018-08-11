"""GNOME Shell plugin"""
import os
from time import sleep
from typing import List

import dbus
from larry import Color, ConfigType, rgb, rgba, rrggbb, write_file

# Has this plugin been run before?
_FIRST_RUN = False


def plugin(colors: List[Color], config: ConfigType) -> None:
    """gnome_shell plugin for larry"""
    theme_color = colors[0]
    template = os.path.expanduser(config['template'])
    outfile = os.path.expanduser(config['location'])
    config_colors = config.get('colors', '').split()

    with open(template) as myfile:
        orig_css = myfile.read()

    new_css = orig_css

    for color in config_colors:
        num_commas = color.count(',')

        if num_commas == 0:
            # rrggbb
            new_css = rrggbb(color, theme_color, new_css)
        elif num_commas == 2:
            # r,g,b
            new_css = rgb(color, theme_color, new_css)
        elif num_commas == 3:
            # r,g,b,a
            new_css = rgba(color, theme_color, new_css)

    write_file(outfile, new_css)

    # tell gnome shell to reload the theme
    gnome_shell_reload_theme()


def gnome_shell_reload_theme() -> None:
    global _FIRST_RUN

    if _FIRST_RUN:
        # If larry is in your autostart, gnome-shell might not be
        # initialized all the way before this function is called.
        # Calling it too soon causes the original theme to not always
        # get loaded properly. We give it some time.
        sleep(10)
        _FIRST_RUN = False

    bus = dbus.SessionBus()
    obj = bus.get_object('org.gnome.Shell', '/org/gnome/Shell')
    obj_iface = dbus.Interface(obj, 'org.gnome.Shell')
    obj_iface.Eval('Main.loadTheme();')
