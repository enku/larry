"""Larry's CLI interface"""
import argparse
import asyncio
import functools
import logging
import os
import signal
import sys

import aionotify

from larry import CONFIG, CONFIG_PATH, LOGGER, PluginNotFound, __version__, load_algo
from larry.io import read_file, watch_file, write_file
from larry.plugins import do_plugin
from larry.types import Color, RasterImage, SVGImage

HANDLER = None
INTERVAL = 8 * 60


def parse_args(args: tuple) -> argparse.Namespace:
    """Parse command-line arguments"""
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
    colors_str = CONFIG["larry"].get("colors", "").strip().split()

    if colors_str:
        LOGGER.debug("using colors from config")
        colors = [Color(i.strip()) for i in colors_str]
    else:
        colors = orig_colors.copy()
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

    if colors != orig_colors:
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


def main(args=None):
    """Main program entry point"""
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
