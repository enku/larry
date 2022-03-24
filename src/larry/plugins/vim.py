"""Larry plugin for vim"""
import asyncio
import json
from collections.abc import Iterator
from dataclasses import dataclass
from typing import List, Optional, Tuple
from weakref import WeakSet

from larry import LOGGER, Color, ColorList, ConfigType


@dataclass
class HighlightGroup:
    name: str
    key: str
    color: Color


def plugin(colors: ColorList, config: ConfigType) -> None:
    """vim plugin"""

    if not VimProtocol.is_running:
        start(config)

    conversions = config.get("colors", "")
    new_colors = get_new_colors(conversions, colors)
    VimProtocol.run(new_colors, config)


def start(config: ConfigType) -> None:
    address = config.get("listen_address", "localhost")
    port = int(config["port"])

    LOGGER.debug("Starting vim server on %s:%s", address, port)

    loop = asyncio.get_event_loop()
    server = loop.create_server(VimProtocol, address, port)

    loop.create_task(server)


def get_new_colors(config: str, from_colors: ColorList):
    bg_color = from_colors[0]
    vim_configs = [*process_config(config)]
    targets = Color.generate_from(list(from_colors), len(vim_configs))
    to_colors: List[Tuple[str, str]] = []

    for vim_config in vim_configs:
        target = next(targets) if vim_config.key == "fg" else bg_color
        to_color = vim_config.color.colorify(target)
        key = f"gui{vim_config.key}"

        to_colors.append((vim_config.name, f"{key}={to_color}"))

    LOGGER.debug("vim colors: %s", to_colors)

    return to_colors


def process_config(config: str) -> Iterator[HighlightGroup]:
    lines = config.split("\n")

    for line in lines:
        vim_config = process_line(line)

        if vim_config:
            yield vim_config


def process_line(line: str) -> Optional[HighlightGroup]:
    line = line.strip()

    if not line:
        return None

    name, delim, value = line.partition(":")

    if not delim:
        return None

    key, delim, value = value.partition("=")

    if not delim:
        return None

    key = key.strip()
    value = value.strip()
    color = Color("#" + value)

    return HighlightGroup(name=name, key=key, color=color)


class VimProtocol(asyncio.Protocol):
    """vim asyncio Protocol

    Basically all we do is `send_colors` to the clients.  We don't process
    any of their input.  The class has the `run` method which the `vim`
    plugin uses to signal the sending of colors to the clients.
    """

    clients = WeakSet()
    colors: List[Tuple[str, str]] = []
    is_running = False

    def __init__(self):
        self.transport = None

    @staticmethod
    def encode(data):
        """json encode *data* and prepare it for transmission"""
        return json.dumps(data).encode()

    @classmethod
    def send(cls, data, transport):
        """encode *data* as JSON and send it over *transport*"""
        return transport.write(cls.encode(data) + b"\n")

    def connection_made(self, transport):
        self.transport = transport

        self.clients.add(transport)
        self.set_termguicolors(transport)

        if self.colors:
            self.send_colors(transport)

    def connection_lost(self, exc):
        self.clients.remove(self.transport)

    @classmethod
    def send_colors(cls, transport):
        colors = cls.colors

        for label, colorspec in colors:
            vi_cmd = f"hi {label} {colorspec}"
            cls.send(["ex", vi_cmd], transport)

        cls.send(["redraw", ""], transport)

    @classmethod
    def set_termguicolors(cls, transport):
        cls.send(["ex", "set termguicolors"], transport)

    @classmethod
    def run(cls, colors: List[Tuple[str, str]], _):
        cls.is_running = True
        cls.colors = colors
        loop = asyncio.get_event_loop()

        for client in cls.clients:
            loop.call_soon(cls.send_colors, client)
