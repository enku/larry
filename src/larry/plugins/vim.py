"""Larry plugin for vim"""

import asyncio
import json
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, cast
from weakref import WeakSet

from larry import LOGGER, Color, ColorList
from larry.config import ConfigType
from larry.plugins import apply_plugin_filter


@dataclass(frozen=True, slots=True)
class HighlightGroup:
    """vim highlightgroup"""

    name: str
    key: str
    color: Color


def plugin(colors: ColorList, config: ConfigType) -> None:
    """vim plugin"""

    if not VimProtocol.is_running:
        start(config)

    conversions = config.get("colors", "")
    new_colors = get_new_colors(conversions, colors, config)
    VimProtocol.run(new_colors, config)


def start(config: ConfigType) -> None:
    """Start the vim channel server"""
    address = config.get("listen_address", "localhost")
    port = int(config["port"])

    LOGGER.debug("Starting vim server on %s:%s", address, port)

    loop = asyncio.get_event_loop()
    server = loop.create_server(VimProtocol, address, port)

    loop.create_task(server)


def get_new_colors(
    conversions: str, from_colors: ColorList, config: ConfigType
) -> List[Tuple[str, str]]:
    """Given the conversions and colors, return the vim colorscheme"""
    bg_color = from_colors[0]
    vim_configs = [*process_config(conversions)]
    targets = Color.generate_from(list(from_colors), len(vim_configs))
    to_colors = apply_plugin_filter(
        [
            vim_config.color.colorify(target if vim_config.key == "fg" else bg_color)
            for vim_config, target in zip(vim_configs, targets)
        ],
        config,
    )
    vim_colors: List[Tuple[str, str]] = []

    for vim_config, color in zip(vim_configs, to_colors):
        key = f"gui{vim_config.key}"
        vim_colors.append((vim_config.name, f"{key}={color}"))

    LOGGER.debug("vim colors: %s", vim_colors)

    return vim_colors


def process_config(config: str) -> Iterator[HighlightGroup]:
    """Process the color config and return the HighlightGroups"""
    lines = config.split("\n")

    for line in lines:
        vim_config = process_line(line)

        if vim_config:
            yield vim_config


def process_line(line: str) -> Optional[HighlightGroup]:
    """Given the line return the HighlightGroup or None"""
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

    clients: WeakSet[asyncio.BaseTransport] = WeakSet()
    colors: List[Tuple[str, str]] = []
    is_running = False

    def __init__(self) -> None:
        self.transport: Optional[asyncio.WriteTransport] = None

    @staticmethod
    def encode(data) -> bytes:
        """json encode *data* and prepare it for transmission"""
        return json.dumps(data).encode()

    @classmethod
    def send(cls, data: Any, transport: asyncio.BaseTransport) -> None:
        """encode *data* as JSON and send it over *transport*"""
        transport = cast(asyncio.WriteTransport, transport)
        return transport.write(cls.encode(data) + b"\n")

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Called when a connection is made."""
        self.clients.add(transport)
        self.set_termguicolors(transport)

        if self.colors:
            self.send_colors(transport)

    @classmethod
    def send_colors(cls, transport: asyncio.BaseTransport) -> None:
        """Send the current colorscheme to the given transport"""
        colors = cls.colors

        for label, colorspec in colors:
            vi_cmd = f"hi {label} {colorspec}"
            cls.send(["ex", vi_cmd], transport)

        cls.send(["redraw", ""], transport)

    @classmethod
    def set_termguicolors(cls, transport: asyncio.BaseTransport) -> None:
        """Sent the "set termguicolors" command to the given transport"""
        cls.send(["ex", "set termguicolors"], transport)

    @classmethod
    def run(cls, colors: List[Tuple[str, str]], _config: ConfigType) -> None:
        """Iterate over connected clients sending the current colorscheme"""
        cls.is_running = True
        cls.colors = colors
        loop = asyncio.get_event_loop()

        for client in cls.clients:
            loop.call_soon(cls.send_colors, client)
