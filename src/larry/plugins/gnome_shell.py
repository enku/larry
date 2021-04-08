"""GNOME Shell plugin"""
from time import sleep

from larry import Color, ColorList, ConfigType
from larry.color import replace_string
from larry.io import read_file, write_file


def plugin(colors: ColorList, config: ConfigType) -> None:
    """gnome_shell plugin for larry"""
    theme_color = next(Color.generate_from(colors, 1, randomize=False))
    template = config["template"]
    outfile = config["location"]
    config_colors = config.get("colors", "").split()

    orig_css = read_file(template).decode()
    new_css = orig_css

    for color in config_colors:
        new_css = replace_string(new_css, color, theme_color)

    write_file(outfile, new_css.encode())

    # tell gnome shell to reload the theme
    gnome_shell_reload_theme()


# Has this plugin been run before?
plugin.has_run = False


def gnome_shell_reload_theme() -> None:
    """Tell gnome shell to reload the theme"""
    import dbus  # pylint: disable=import-outside-toplevel

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
