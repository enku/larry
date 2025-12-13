# pylint: disable=missing-docstring
import argparse
import contextlib
import io
import os.path
import signal
from unittest import IsolatedAsyncioTestCase, TestCase, mock

from unittest_fixtures import Fixtures, given

from larry import cli, filters
from larry.image import make_image_from_bytes
from larry.io import read_file

from . import lib

ANY = mock.ANY


class HandlerTests(TestCase):
    def tearDown(self):
        cli.Handler.set(None)
        super().tearDown()

    def test(self):
        self.assertEqual(cli.Handler.get(), None)

        cli.Handler.set(6)
        self.assertEqual(cli.Handler.get(), 6)


class BuildParserTests(TestCase):
    def test(self):
        parser = cli.build_parser()
        args = parser.parse_args([])

        self.assertIsInstance(parser, argparse.ArgumentParser)
        self.assertTrue(isinstance(args.config_path, str))
        self.assertIs(False, args.debug)
        self.assertEqual(cli.INTERVAL, args.interval)
        self.assertIs(False, args.list_plugins)
        self.assertIs(False, args.list_filters)


@given(lib.configmaker)
@mock.patch.object(cli, "do_plugin")
class RunTests(IsolatedAsyncioTestCase):
    async def test_runs_filters_and_schedules_plugins(
        self, do_plugin, fixtures: Fixtures
    ) -> None:
        configmaker = fixtures.configmaker
        configmaker.add_config(plugins="command dummy", filter="inverse pastelize")

        await cli.run(configmaker.path)

        self.assertTrue(os.path.exists(configmaker.config["larry"]["output"]))
        pastelize = filters.load_filter("pastelize")
        inverse = filters.load_filter("inverse")
        colors = pastelize(
            inverse(
                lib.make_colors("#000000 #1c343f #254351 #666666 #7c8e96 #ffffff"), ANY
            ),
            ANY,
        )
        do_plugin.assert_has_calls(
            [
                mock.call("command", colors, configmaker.path),
                mock.call("dummy", colors, configmaker.path),
            ]
        )

    async def test_pause_mode_does_nothing(
        self, _do_plugin: mock.Mock, fixtures: Fixtures
    ) -> None:
        configmaker = fixtures.configmaker
        configmaker.add_config(
            pause="1", plugins="command dummy", filter="inverse pastelize"
        )

        loop = mock.Mock()
        await cli.run(configmaker.path)

        self.assertFalse(os.path.exists(configmaker.config["larry"]["output"]))
        loop.call_soon.assert_not_called()

    @mock.patch("larry.cli.LOGGER")
    async def test_logs_invalid_filters(
        self, logger, _do_plugin: mock.Mock, fixtures: Fixtures
    ) -> None:
        configmaker = fixtures.configmaker
        configmaker.add_config(filter="inverse bogus pastelize")

        await cli.run(configmaker.path)

        logger.exception.assert_called_once_with(
            "Color filter bogus not found. Skipping."
        )

        pastelize = filters.load_filter("pastelize")
        inverse = filters.load_filter("inverse")
        colors = pastelize(
            inverse(
                lib.make_colors("#000000 #1c343f #254351 #666666 #7c8e96 #ffffff"), ANY
            ),
            ANY,
        )
        image = make_image_from_bytes(read_file(configmaker.config["larry"]["output"]))
        image_colors = image.colors
        self.assertEqual(set(colors), set(image_colors))

    async def test_colors_from_config(
        self, _do_plugin: mock.Mock, fixtures: Fixtures
    ) -> None:
        configmaker = fixtures.configmaker
        color_str = "red white blue pink yellow"
        configmaker.add_config(colors=color_str, filter="none")

        await cli.run(configmaker.path)

        image = make_image_from_bytes(read_file(configmaker.config["larry"]["output"]))
        image_colors = image.colors
        colors = lib.make_colors(color_str)
        self.assertEqual(set(colors), set(image_colors))

    async def test_run_with_no_config(
        self, _do_plugin: mock.Mock, fixtures: Fixtures
    ) -> None:
        with mock.patch("larry.cli.write_file") as write_file:
            await cli.run(f"{fixtures.tmpdir}/bogus.cfg")

        write_file.assert_called()


@given(lib.configmaker)
class RunEveryTests(IsolatedAsyncioTestCase):
    async def test_runs_and_schedules_to_run_again(self, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        with mock.patch("larry.cli.Handler") as mock_handler:
            mock_handler.get.return_value = None
            with mock.patch("larry.cli.asyncio.get_running_loop") as get_running_loop:
                await cli.run_every(15.0, configmaker.path)

        self.assertTrue(os.path.exists(configmaker.config["larry"]["output"]))
        loop = get_running_loop.return_value
        loop.call_later.assert_called_once_with(15.0, mock.ANY)
        timer_handler = loop.call_later.return_value
        mock_handler.set_assert_called_once_with(timer_handler)

    async def test_runs_only_once_with_interval_0(self, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        with mock.patch("larry.cli.Handler") as mock_handler:
            mock_handler.get.return_value = None
            loop = mock.Mock()
            await cli.run_every(0, configmaker.path)

        loop.call_later.assert_not_called()

    async def test_cancel_existing_handler(self, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        with mock.patch("larry.cli.Handler") as mock_handler:
            handler = mock.Mock()
            mock_handler.get.return_value = handler
            await cli.run_every(15.0, configmaker.path)

        handler.cancel.assert_called_once_with()


@given(lib.configmaker, stop=lambda _: cli.STOP_EVENT.set())
@mock.patch("larry.cli.asyncio.get_running_loop")
class MainTests(IsolatedAsyncioTestCase):
    async def test(self, get_running_loop: mock.Mock, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        args = cli.parse_args(f"larry -c {configmaker.path} --interval=60".split())
        assert args

        await cli.main(args)

        loop = get_running_loop.return_value
        loop.add_signal_handler.assert_called_once_with(signal.SIGUSR1, mock.ANY)

    async def test_with_interval_0(
        self, get_running_loop: mock.Mock, fixtures: Fixtures
    ) -> None:
        configmaker = fixtures.configmaker
        args = cli.parse_args(f"larry -c {configmaker.path} -n0".split())

        await cli.main(args)

        loop = get_running_loop.return_value
        loop.add_signal_handler.assert_called_once_with(signal.SIGUSR1, mock.ANY)

    async def test_with_debug(
        self, _get_running_loop: mock.Mock, fixtures: Fixtures
    ) -> None:
        configmaker = fixtures.configmaker
        args = cli.parse_args(f"larry -c {configmaker.path} --debug".split())

        with mock.patch("larry.cli.LOGGER") as logger:
            await cli.main(args)

        logger.setLevel.assert_called_once_with("DEBUG")

    async def test_list_filters(
        self, _get_running_loop: mock.Mock, fixtures: Fixtures
    ) -> None:
        configmaker = fixtures.configmaker
        argv = f"larry -c {configmaker.path} --list-filters".split()
        args = cli.parse_args(argv)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            await cli.main(args)

        self.assertIn("[X] gradient", stdout.getvalue())

    async def test_list_plugins(
        self, _get_running_loop: mock.Mock, fixtures: Fixtures
    ) -> None:
        configmaker = fixtures.configmaker
        configmaker.add_config(plugins="command")
        argv = f"larry -c {configmaker.path} --list-plugins".split()
        args = cli.parse_args(argv)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            await cli.main(args)

        self.assertIn("[X] command", stdout.getvalue())
