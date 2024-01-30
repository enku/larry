"""Larry's CLI interface"""

import argparse
import asyncio
import logging
import os
import signal
import sys
from typing import Sequence

import daemon

from larry import LOGGER, Color, __version__, make_image_from_bytes
from larry.config import DEFAULT_CONFIG_PATH
from larry.config import load as load_config
from larry.filters import FilterNotFound, list_filters, load_filter
from larry.io import read_file, write_file
from larry.plugins import do_plugin, list_plugins

INTERVAL = 8 * 60


class Handler:
    """Process timer handle"""

    _handler = None

    @classmethod
    def get(cls) -> asyncio.TimerHandle | None:
        return cls._handler

    @classmethod
    def set(cls, handler: asyncio.TimerHandle | None) -> None:
        cls._handler = handler


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--config", "-c", type=str, dest="config_path", default=DEFAULT_CONFIG_PATH
    )
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--interval", "-n", type=int, default=INTERVAL)
    parser.add_argument(
        "--list-plugins", action="store_true", default=False, help="List known plugins"
    )
    parser.add_argument(
        "--list-filters", action="store_true", default=False, help="List known filters"
    )
    parser.add_argument(
        "--daemonize",
        "-d",
        action="store_true",
        default=False,
        help="Run as a background daemon",
    )

    return parser.parse_args(argv)


def run(config_path: str) -> None:
    """Perform a single iteration of Larry"""
    config = load_config(config_path)

    if config["larry"].getboolean("pause", False):
        LOGGER.info("Larry is paused")
        return

    raw_image_data = read_file(os.path.expanduser(config["larry"]["input"]))
    image = make_image_from_bytes(raw_image_data)

    orig_colors = list(image.get_colors())
    orig_colors.sort(key=Color.luminocity)
    colors_str = config["larry"].get("colors", "").strip().split()

    if colors_str:
        LOGGER.debug("using colors from config")
        colors = [Color(i.strip()) for i in colors_str]
    else:
        colors = orig_colors.copy()
        filter_names = config["larry"].get("filter", "gradient").split()

        for filter_name in filter_names:
            try:
                filter_ = load_filter(filter_name)
            except FilterNotFound:
                error_message = f"Color filter {filter_name} not found. Skipping."
                LOGGER.exception(error_message)
            else:
                LOGGER.debug("Calling filter %s", filter_name)
                colors = filter_(colors, config)

    LOGGER.debug("new colors: %s", colors)

    if colors != orig_colors:
        image = image.replace(orig_colors, colors)

    outfile = os.path.expanduser(config["larry"]["output"])
    write_file(outfile, bytes(image))

    # now run any plugins
    plugins = config["larry"].get("plugins", "").split()
    loop = asyncio.get_event_loop()

    for plugin_name in plugins:
        loop.call_soon(do_plugin, plugin_name, [*colors], config_path)


def run_every(interval: float, config_path: str, loop) -> None:
    """Run *callback* immediately and then every *interval* seconds after"""
    if handler := Handler.get():
        LOGGER.info("received signal to change wallpaper")
        handler.cancel()

    run(config_path)

    if interval == 0:
        return

    handler = loop.call_later(interval, run_every, interval, config_path, loop)
    Handler.set(handler)


def main(args=None) -> None:
    """Main program entry point"""
    args = parse_args(args if args is not None else sys.argv[1:])

    if args.daemonize:
        with daemon.DaemonContext():
            real_main(args)
    else:
        real_main(args)


def real_main(args) -> None:
    """Actual program entry point"""
    logging.basicConfig()
    config = load_config(args.config_path)

    if args.debug or config["larry"].getboolean("debug", fallback=False):
        LOGGER.setLevel("DEBUG")

    LOGGER.debug("args=%s", args)

    if args.list_plugins:
        print(list_plugins(args.config_path), end="")
        return

    if args.list_filters:
        print(list_filters(args.config_path), end="")
        return

    loop = asyncio.get_event_loop()

    if args.interval:
        loop.add_signal_handler(
            signal.SIGUSR1, run_every, args.interval, args.config_path, loop
        )
        loop.call_soon(run_every, args.interval, args.config_path, loop)
    else:
        loop.add_signal_handler(signal.SIGUSR1, run, args.config_path)
        run(args.config_path)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        LOGGER.info("User interrupted")
        loop.stop()
    finally:
        loop.close()
