"""Larry plugin for vim"""
import asyncio
import json
from typing import Generator, List, Optional, Tuple
from weakref import WeakSet

from larry import LOGGER, Color, ConfigType

_IS_RUNNING = False


def plugin(colors: List[Color], config: ConfigType) -> None:
    """vim plugin"""
    global _IS_RUNNING

    if not _IS_RUNNING:
        start(config)
        _IS_RUNNING = True

    new_colors = get_new_colors(config["colors"], colors)
    VimProtocol.run(new_colors, config)


def start(config):
    address = config.get("listen_address", "localhost")
    port = int(config["port"])

    LOGGER.debug("Starting vim server on %s:%s", address, port)

    loop = asyncio.get_event_loop()
    server = loop.create_server(VimProtocol, address, port)

    loop.create_task(server)


def get_new_colors(config, from_colors):
    bg_color = from_colors[0]
    fg_color = from_colors[-1]
    to_colors = []

    for group, layer, color in process_config(config):
        target = fg_color if layer == "fg" else bg_color
        to_color = color.colorify(target)
        key = f"gui{layer}"

        to_colors.append((group, f"{key}={to_color}"))

    LOGGER.debug("vim colors: %s", to_colors)

    return to_colors


def process_config(config: str) -> Generator[Tuple[str, str, Color], None, None]:
    lines = config.split("\n")

    for line in lines:
        triplet = process_line(line)

        if triplet:
            yield triplet


def process_line(line: str) -> Optional[Tuple[str, str, Color]]:
    line = line.strip()

    if not line:
        return None

    group, delim, value = line.partition(":")

    if not delim:
        return None

    layer, delim, value = value.partition("=")

    if not delim:
        return None

    layer = layer.strip()
    value = value.strip()
    color = Color("#" + value)

    return (group, layer, color)


class VimProtocol(asyncio.Protocol):
    """vim asyncio Protocol

    Basically all we do is `send_colors` to the clients.  We don't process
    any of their input.  The class has the `run` method which the `vim`
    plugin uses to signal the sending of colors to the clients.
    """

    clients = WeakSet()
    colors = None

    def __init__(self):
        self.transport = None

    @staticmethod
    def encode(data):
        """json encode *data* and prepare it for transmission"""
        return json.dumps(data).encode()

    @classmethod
    def send(cls, data, transport):
        """encode *data* as JSON and send it over *transport*"""
        return transport.write(cls.encode(data))

    def connection_made(self, transport):
        self.transport = transport

        self.clients.add(transport)
        self.set_termguicolors(transport)

        if self.colors:
            self.send_colors(transport)

    @classmethod
    def send_colors(cls, transport):
        colors = cls.colors

        for label, colorspec in colors:
            vi_cmd = f"hi {label} {colorspec}"
            cls.send(["ex", vi_cmd], transport)

    @classmethod
    def set_termguicolors(cls, transport):
        cls.send(["ex", "set termguicolors"], transport)

    @classmethod
    def run(cls, colors, _):
        cls.colors = colors
        loop = asyncio.get_event_loop()

        for client in cls.clients:
            loop.call_soon(cls.send_colors, client)
