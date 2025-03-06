# pylint: disable=missing-docstring
import random
from unittest import TestCase, mock

from unittest_fixtures import Fixtures, given

from larry.plugins import vim

from . import make_colors

COLORS = list(
    make_colors("#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9")
)
COLOR_STR = """
" Comment
ALEErrorSign: bg=073642
ALEWarningSign: bg=073642
ColorColumn: bg=073642
ColorColumn: fg=576D74
CommandTSelection: bg=4a90d9
Comment: fg=FF6600
Constant: fg=339999
invalid: definition
"""

CONVERSION = [
    ("ALEErrorSign", "guibg=#3a0742"),
    ("ALEWarningSign", "guibg=#3a0742"),
    ("ColorColumn", "guibg=#3a0742"),
    ("ColorColumn", "guifg=#745769"),
    ("CommandTSelection", "guibg=#c549d9"),
    ("Comment", "guifg=#4e00ff"),
    ("Constant", "guifg=#8b3399"),
]


@given("random", "config")
class PluginTests(TestCase):
    @mock.patch("larry.plugins.vim.start")
    @mock.patch("larry.plugins.vim.VimProtocol.run")
    def test(self, run, start, fixtures: Fixtures) -> None:
        config = fixtures.config
        config.add_section("plugins:vim")
        config.add_config(
            listen_address="localhost.invalid", port=65336, colors=COLOR_STR
        )
        vim.plugin(COLORS, config.config["plugins:vim"])
        start.assert_called_once_with(config.config["plugins:vim"])
        run.assert_called_once_with(CONVERSION, config.config["plugins:vim"])


@given("config")
class StartTests(TestCase):
    @mock.patch("larry.plugins.vim.asyncio.get_event_loop")
    def test(self, get_event_loop, fixtures: Fixtures) -> None:
        config = fixtures.config
        config.add_section("plugins:vim")
        config.add_config(listen_address="localhost.invalid", port=65336)

        vim.start(config.config["plugins:vim"])

        get_event_loop.assert_called_once_with()
        loop = get_event_loop.return_value
        loop.create_server.assert_called_once_with(
            vim.VimProtocol, "localhost.invalid", 65336
        )
        server = loop.create_server.return_value
        loop.create_task.assert_called_once_with(server)


@mock.patch("larry.color.random", random.Random(1))
class GetNewColorsTests(TestCase):
    def test(self):
        new_colors = vim.get_new_colors(COLOR_STR, COLORS)

        self.assertEqual(new_colors, CONVERSION)

    def test_with_soften(self):
        new_colors = vim.get_new_colors(COLOR_STR, COLORS, soften=True)

        expected = [
            ("ALEErrorSign", "guibg=#9658a0"),
            ("ALEWarningSign", "guibg=#9658a0"),
            ("ColorColumn", "guibg=#9658a0"),
            ("ColorColumn", "guifg=#a2b7b9"),
            ("CommandTSelection", "guibg=#e19deb"),
            ("Comment", "guifg=#ffec7f"),
            ("Constant", "guifg=#ccc688"),
        ]
        self.assertEqual(new_colors, expected)


class VimProtocolTests(TestCase):
    def tearDown(self):
        vim.VimProtocol.clients.clear()
        vim.VimProtocol.colors = []
        vim.VimProtocol.is_running = False

        super().tearDown()

    def test_encode_data(self):
        data = {"foo": "bar"}

        result = vim.VimProtocol.encode(data)

        self.assertEqual(result, b'{"foo": "bar"}')

    def test_connection_made(self):
        transport = mock.Mock()
        vim.VimProtocol.colors = CONVERSION
        vp = vim.VimProtocol()

        vp.connection_made(transport)

        self.assertEqual(transport.write.call_count, len(CONVERSION) + 2)
        self.assertEqual(
            transport.write.mock_calls[0], mock.call(b'["ex", "set termguicolors"]\n')
        )
        self.assertIn(transport, vp.clients)

    def test_send(self):
        data = "it's all good"
        transport = mock.Mock()

        result = vim.VimProtocol.send(data, transport)

        transport.write.assert_called_once_with(b'"it\'s all good"\n')
        self.assertEqual(result, transport.write.return_value)

    def test_send_colors(self):
        transport = mock.Mock()
        vim.VimProtocol.colors = CONVERSION

        vim.VimProtocol.send_colors(transport)

        self.assertEqual(transport.write.call_count, len(CONVERSION) + 1)
        transport.write.assert_called_with(b'["redraw", ""]\n')

    def test_set_termguicolors(self):
        transport = mock.Mock()

        vim.VimProtocol.set_termguicolors(transport)

        transport.write.assert_called_once_with(b'["ex", "set termguicolors"]\n')

    @mock.patch("larry.plugins.vim.asyncio.get_event_loop")
    def test_run(self, get_event_loop):
        vp = vim.VimProtocol()

        client = mock.Mock()
        with mock.patch.object(vim.VimProtocol, "clients", [client]):
            vp.run(CONVERSION, None)

        self.assertTrue(vim.VimProtocol.is_running)
        self.assertEqual(vim.VimProtocol.colors, CONVERSION)

        loop = get_event_loop.return_value
        loop.call_soon.assert_called_once_with(vim.VimProtocol.send_colors, client)
