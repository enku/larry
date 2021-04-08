"""Larry's CLI interface"""
import argparse
import asyncio
import logging
import os
import signal
import sys

from larry import LOGGER, Color, Image, __version__, load_config
from larry.algos import AlgoNotFound, algos_list, load_algo
from larry.io import read_file, write_file
from larry.plugins import PluginNotFound, do_plugin, plugins_list

HANDLER = None
INTERVAL = 8 * 60


def parse_args(args: tuple) -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--interval", "-n", type=int, default=INTERVAL)
    parser.add_argument(
        "--list-plugins", action="store_true", default=False, help="List known plugins"
    )
    parser.add_argument(
        "--list-algos", action="store_true", default=False, help="List known algos"
    )

    return parser.parse_args(args)


def run() -> None:
    config = load_config()
    raw_image_data = read_file(os.path.expanduser(config["larry"]["input"]))
    image = Image.from_bytes(raw_image_data)

    orig_colors = list(image.get_colors())
    orig_colors.sort(key=Color.luminocity)
    colors_str = config["larry"].get("colors", "").strip().split()

    if colors_str:
        LOGGER.debug("using colors from config")
        colors = [Color(i.strip()) for i in colors_str]
    else:
        colors = orig_colors.copy()
        algo_names = config["larry"].get("algo", "gradient").split()

        for algo_name in algo_names:
            try:
                algo = load_algo(algo_name)
            except AlgoNotFound:
                error_message = f"Color algo {algo_name} not found. Skipping."
                LOGGER.exception(error_message)
            else:
                LOGGER.debug("Calling algo %s", algo_name)
                colors = algo(colors, config)

    LOGGER.debug("new colors: %s", colors)

    if colors != orig_colors:
        image.replace(orig_colors, colors)

    outfile = os.path.expanduser(config["larry"]["output"])
    write_file(outfile, bytes(image))

    # now run any plugins
    if "larry" not in config.sections():
        return

    plugins = config["larry"].get("plugins", "").split()
    loop = asyncio.get_event_loop()

    for plugin_name in plugins:
        loop.call_soon(do_plugin, plugin_name, colors)


def run_every(interval: float, loop) -> None:
    """Run *callback* immediately and then every *interval* seconds after"""
    global HANDLER

    if HANDLER:
        LOGGER.info("received signal to change wallpaper")
        HANDLER.cancel()

    run()

    if interval == 0:
        return

    HANDLER = loop.call_later(interval, run_every, interval, loop)


def list_plugins(output=sys.stdout):
    """List all the beautiful plugins"""
    config = load_config()
    enabled_plugins = config["larry"].get("plugins", "").split()

    for name, func in plugins_list():
        doc = func.__doc__.split("\n", 1)[0].strip()
        enabled = "X" if name in enabled_plugins else " "
        print(f"[{enabled}] {name:20} {doc}", file=output)


def list_algos(output=sys.stdout):
    config = load_config()
    enabled_algo = config["larry"].get("algo", "gradient").split()

    for name, func in algos_list():
        doc = func.__doc__.split("\n", 1)[0].strip()
        enabled = "X" if name in enabled_algo else " "

        print(f"[{enabled}] {name:20} {doc}", file=output)


def main(args=None):
    """Main program entry point"""
    args = parse_args(args or sys.argv[1:])

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    LOGGER.debug("args=%s", args)

    if args.list_plugins:
        list_plugins()
        return

    if args.list_algos:
        list_algos()
        return

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGUSR1, run_every, args.interval, loop)
    loop.call_soon(run_every, args.interval, loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        LOGGER.info("User interrupted")
        loop.stop()
    finally:
        loop.close()
