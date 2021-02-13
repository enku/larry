"""Replace colors on the Larry the Cow wallpaper"""
import argparse
import asyncio
import configparser
import functools
import logging
import operator
import os
import random
import re
import signal
import subprocess
import sys
from typing import Callable, List, MutableMapping, Optional, Set, Tuple, TypeVar, Union

import aionotify
import pkg_resources

from larry.types import Color, RasterImage, SVGImage

__version__ = "1.6.1"

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
ORIG_FILENAME = os.path.join(DATA_DIR, "gentoo-cow-gdm-remake.svg")
INTERVAL = 8 * 60
LOGGER = logging.getLogger("larry")
HANDLER = None
CONFIG_PATH = os.path.expanduser("~/.config/larry.cfg")
CONFIG = configparser.ConfigParser()
CONFIG["DEFAULT"]["input"] = ORIG_FILENAME
CONFIG["DEFAULT"]["fuzz"] = "10"
CONFIG.read(CONFIG_PATH)

ConfigType = MutableMapping[str, str]
PluginType = Callable[[List["Color"], ConfigType], None]

PLUGINS = {}  # type: MutableMapping[str, PluginType]


class PluginNotFound(LookupError):
    """Unable to find the requested plugin"""


def parse_args(args: tuple) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("--input", "-i", default=None)
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--fuzz", "-f", type=int, default=0)
    parser.add_argument("--interval", "-n", type=int, default=INTERVAL)
    parser.add_argument("output", type=str)

    return parser.parse_args(args)


def read_file(filename: str) -> bytes:
    pipe_exec = filename.startswith("!")

    if pipe_exec:
        popen = subprocess.Popen(
            os.path.expanduser(filename[1:]), shell=True, stdout=subprocess.PIPE
        )
        content = popen.stdout.read()
    else:
        with open(os.path.expanduser(filename), "rb") as myfile:
            content = myfile.read()

    return content


def write_file(filename: str, data: bytes) -> int:
    """write open *filename* and write *text* to it"""
    with open(filename, "wb") as myfile:
        return myfile.write(data)


async def watch_file(watcher: aionotify.Watcher, loop, handler):
    try:
        await watcher.setup(loop)
    except OSError as error:
        LOGGER.warning(error)

        return

    while True:
        await watcher.get_event()
        handler()


def randsign(num: int) -> int:
    return random.choice([-1, 1]) * random.randint(0, num)


def run(reload_config: bool = False) -> None:
    if reload_config:
        CONFIG.read(CONFIG_PATH)

    raw_image_data = read_file(os.path.expanduser(CONFIG["larry"]["input"]))
    try:
        image = SVGImage(raw_image_data)
    except UnicodeDecodeError:
        image = RasterImage(raw_image_data)

    orig_colors = list(image.get_colors())
    orig_colors.sort(key=Color.luminocity)
    orig_colors = [i for i in orig_colors if i.luminocity() not in (0, 255)]
    fuzz = CONFIG.getint("larry", "fuzz")
    lum1 = max([orig_colors[0].luminocity() + randsign(fuzz), 1])
    lum2 = min([orig_colors[-1].luminocity() + randsign(fuzz), 254])
    colors_str = CONFIG["larry"].get("colors", "").strip().split()

    if colors_str:
        LOGGER.debug("using colors from config")
        colors = [Color(i.strip()) for i in colors_str]
    else:
        colors = orig_colors[:]
        algo_names = CONFIG["larry"].get("algo", "gradient").split()

        for algo_name in algo_names:
            try:
                algo = load_algo(algo_name)
            except PluginNotFound:
                error_message = f"Color algo {algo_name} not found. Skipping."
                sys.stderr.write(error_message)
            else:
                colors = algo(colors, CONFIG)

    LOGGER.debug("new colors: %s", colors)

    image.replace(orig_colors, colors)

    outfile = CONFIG["larry"]["output"]
    write_file(outfile, bytes(image))

    # now run any plugins
    if "larry" not in CONFIG.sections():
        return

    plugins = CONFIG["larry"].get("plugins", "").split()
    loop = asyncio.get_event_loop()

    for plugin_name in plugins:
        loop.call_soon(do_plugin, plugin_name, colors)


def do_plugin(plugin_name: str, colors: List[Color]) -> None:
    plugin = load_plugin(plugin_name)
    config = get_plugin_config(plugin_name)

    LOGGER.debug("Running plugin for %s", plugin_name)
    plugin(colors, config)


def get_plugin_config(plugin_name: str) -> ConfigType:
    plugin_config_name = f"plugins:{plugin_name}"

    if plugin_config_name in CONFIG:
        plugin_config = dict(CONFIG[plugin_config_name])
    else:
        plugin_config = {}

    return plugin_config


def load_plugin(name: str):
    if name not in PLUGINS:
        iter_ = pkg_resources.iter_entry_points("larry.plugins", name)

        try:
            plugin = next(iter_).load()
        except (ModuleNotFoundError, StopIteration) as error:
            raise PluginNotFound(name) from error

        PLUGINS[name] = plugin

    return PLUGINS[name]


def load_algo(name: str) -> Callable:
    """Load the algo with the given name"""
    iter_ = pkg_resources.iter_entry_points("larry.algos", name)

    try:
        return next(iter_).load()
    except (ModuleNotFoundError, StopIteration) as error:
        raise PluginNotFound(name) from error


def run_every(interval: float, loop, reload_config: bool = False) -> None:
    """Run *callback* immediately and then every *interval* seconds after"""
    global HANDLER

    if HANDLER:
        LOGGER.warning("received signal to change wallpaper")
        HANDLER.cancel()

    run(reload_config)

    if interval == 0:
        return

    HANDLER = loop.call_later(interval, run_every, interval, loop)


def rrggbb(color: str, theme_color: Color, css: str) -> str:
    color = "#" + color
    orig_color = Color(color)
    new_color = orig_color.colorify(theme_color)

    return re.sub(str(color), str(new_color), css, flags=re.I)


def rgb(color: str, theme_color: Color, css: str) -> str:
    red, green, blue = [int(float(i)) for i in color.split(",")]
    orig_color = Color((red, green, blue))
    new_color = orig_color.colorify(theme_color)
    re_str = re.escape(f"rgb({color})")

    return re.sub(re_str, str(new_color), css, flags=re.I)


def rgba(color: str, theme_color: Color, css: str) -> str:
    parts = color.split(",")
    red, green, blue, *_ = [int(float(i)) for i in parts]
    orig_color = Color((red, green, blue))
    new_color = orig_color.colorify(theme_color)
    re_str = re.escape("rgba({},{},{},".format(*parts[:3]))
    re_str = re_str + r"(" + re.escape(parts[-1]) + r")\)"
    new_str = "rgba({},{},{},\\1)".format(
        new_color.red, new_color.green, new_color.blue
    )

    return re.sub(re_str, new_str, css, flags=re.I)


def init_config():
    if "larry" not in CONFIG:
        CONFIG["larry"] = {}


def main(args=None):
    """Main program entry point"""
    init_config()
    args = parse_args(args or sys.argv[1:])

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    LOGGER.debug("args=%s", args)

    if args.input:
        CONFIG["larry"]["input"] = args.input

    if args.fuzz is not None:
        CONFIG["larry"]["fuzz"] = str(args.fuzz)

    CONFIG["larry"]["output"] = args.output

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGUSR1, run_every, args.interval, loop, True)
    loop.call_soon(run_every, args.interval, loop)

    watcher = aionotify.Watcher()
    watcher.watch(CONFIG_PATH, aionotify.Flags.MODIFY | aionotify.Flags.CREATE)
    loop.create_task(
        watch_file(
            watcher, loop, functools.partial(run_every, args.interval, loop, True)
        )
    )

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        LOGGER.info("User interrupted")
        loop.stop()
    finally:
        loop.close()


if __name__ == "__main__":
    main()
