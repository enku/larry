# pylint: disable=missing-docstring
import argparse
import asyncio
import contextlib
import io
import os.path
import signal
from unittest import TestCase, mock

from unittest_fixtures import Fixtures, given

from larry import cli, filters
from larry.image import make_image_from_bytes
from larry.io import read_file

from . import fixtures as tf
from . import make_colors


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


@given(tf.configmaker)
class RunTests(TestCase):
    def test_runs_filters_and_schedules_plugins(self, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        configmaker.add_config(plugins="command dummy", filter="inverse pastelize")

        loop = mock.Mock()
        cli.run(configmaker.path, loop)

        self.assertTrue(os.path.exists(configmaker.config["larry"]["output"]))
        pastelize = filters.load_filter("pastelize")
        inverse = filters.load_filter("inverse")
        colors = pastelize(
            inverse(
                make_colors("#000000 #1c343f #254351 #666666 #7c8e96 #ffffff"), None
            ),
            None,
        )
        loop.call_soon.assert_has_calls(
            [
                mock.call(cli.do_plugin, "command", colors, configmaker.path),
                mock.call(cli.do_plugin, "dummy", colors, configmaker.path),
            ]
        )

    def test_pause_mode_does_nothing(self, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        configmaker.add_config(
            pause="1", plugins="command dummy", filter="inverse pastelize"
        )

        loop = mock.Mock()
        cli.run(configmaker.path, loop)

        self.assertFalse(os.path.exists(configmaker.config["larry"]["output"]))
        loop.call_soon.assert_not_called()

    @mock.patch("larry.cli.LOGGER")
    def test_logs_invalid_filters(self, logger, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        configmaker.add_config(filter="inverse bogus pastelize")

        loop = mock.Mock()
        cli.run(configmaker.path, loop)

        logger.exception.assert_called_once_with(
            "Color filter bogus not found. Skipping."
        )

        pastelize = filters.load_filter("pastelize")
        inverse = filters.load_filter("inverse")
        colors = pastelize(
            inverse(
                make_colors("#000000 #1c343f #254351 #666666 #7c8e96 #ffffff"), None
            ),
            None,
        )
        image = make_image_from_bytes(read_file(configmaker.config["larry"]["output"]))
        image_colors = image.colors
        self.assertEqual(set(colors), set(image_colors))

    def test_colors_from_config(self, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        color_str = "red white blue pink yellow"
        configmaker.add_config(colors=color_str, filter="none")

        loop = mock.Mock()
        cli.run(configmaker.path, loop)

        image = make_image_from_bytes(read_file(configmaker.config["larry"]["output"]))
        image_colors = image.colors
        colors = make_colors(color_str)
        self.assertEqual(set(colors), set(image_colors))

    def test_run_with_no_config(self, fixtures: Fixtures) -> None:
        with mock.patch("larry.cli.write_file") as write_file:
            cli.run(f"{fixtures.tmpdir}/bogus.cfg", mock.Mock())

        write_file.assert_called()


@given(tf.configmaker)
class RunEveryTests(TestCase):
    def test_runs_and_schedules_to_run_again(self, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        with mock.patch("larry.cli.Handler") as mock_handler:
            mock_handler.get.return_value = None
            loop = mock.Mock()
            cli.run_every(15.0, configmaker.path, loop)

        self.assertTrue(os.path.exists(configmaker.config["larry"]["output"]))
        loop.call_later.assert_called_once_with(
            15.0, cli.run_every, 15.0, configmaker.path, loop
        )
        timer_handler = loop.call_later.return_value
        mock_handler.set_assert_called_once_with(timer_handler)

    def test_runs_only_once_with_interval_0(self, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        with mock.patch("larry.cli.Handler") as mock_handler:
            mock_handler.get.return_value = None
            loop = mock.Mock()
            cli.run_every(0, configmaker.path, loop)

        loop.call_later.assert_not_called()

    def test_cancel_existing_handler(self, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        with mock.patch("larry.cli.Handler") as mock_handler:
            handler = mock.Mock()
            mock_handler.get.return_value = handler
            loop = mock.Mock()
            cli.run_every(15.0, configmaker.path, loop)

        handler.cancel.assert_called_once_with()


@given(tf.configmaker)
@mock.patch("larry.cli.asyncio.new_event_loop")
class MainTests(TestCase):
    def test(self, new_event_loop, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        argv = f"larry -c {configmaker.path} --interval=60".split()

        cli.main(argv)

        loop = new_event_loop.return_value
        loop.add_signal_handler.assert_called_once_with(
            signal.SIGUSR1, cli.run_every, 60, configmaker.path, loop
        )
        loop.call_soon.assert_called_once_with(
            cli.run_every, 60, configmaker.path, loop
        )
        loop.run_forever.assert_called_once_with()
        loop.close.assert_called_once_with()

    def test_with_interval_0(self, new_event_loop, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        argv = f"larry -c {configmaker.path} -n0".split()

        cli.main(argv)

        loop = new_event_loop.return_value
        loop.add_signal_handler.assert_called_once_with(
            signal.SIGUSR1, cli.run, configmaker.path, loop
        )

    def test_keyboard_interrupt_stops_loop(
        self, new_event_loop, fixtures: Fixtures
    ) -> None:
        configmaker = fixtures.configmaker
        argv = f"larry -c {configmaker.path} --interval 60".split()
        loop = new_event_loop.return_value
        loop.run_forever.side_effect = KeyboardInterrupt()

        cli.main(argv)

        loop.stop.assert_called_once_with()

    def test_list_plugins(self, new_event_loop, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        configmaker.add_config(plugins="command")
        argv = f"larry -c {configmaker.path} --list-plugins".split()

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main(argv)

        self.assertIn("[X] command", stdout.getvalue())
        new_event_loop.assert_not_called()

    def test_list_filters(self, new_event_loop, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        argv = f"larry -c {configmaker.path} --list-filters".split()

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main(argv)

        self.assertIn("[X] gradient", stdout.getvalue())
        new_event_loop.assert_not_called()

    @mock.patch("larry.cli.LOGGER")
    def test_with_debug(self, logger, _new_event_loop, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        argv = f"larry -c {configmaker.path} --debug --list-plugins".split()

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main(argv)

        logger.setLevel.assert_called_once_with("DEBUG")


class RunLoopTests(TestCase):
    def test_runs_forever(self) -> None:
        loop = mock.Mock(spec=asyncio.AbstractEventLoop)

        cli.run_loop(loop)

        loop.assert_has_calls(
            [mock.call.run_forever(), mock.call.close()], any_order=False
        )

    def test_intercepts_keyboardinterrupt(self) -> None:
        loop = mock.Mock(spec=asyncio.AbstractEventLoop)
        loop.run_forever.side_effect = KeyboardInterrupt()

        cli.run_loop(loop)

        loop.assert_has_calls(
            [mock.call.run_forever(), mock.call.stop(), mock.call.close()],
            any_order=False,
        )
