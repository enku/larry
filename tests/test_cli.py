# pylint: disable=missing-docstring
import argparse
import contextlib
import io
import signal
from unittest import mock

from larry import cli

from . import TestCase


@mock.patch("larry.cli.real_main")
@mock.patch("larry.cli.daemon.DaemonContext")
class MainTests(TestCase):
    def test_daemonize_false(self, daemon, real_main):
        args = []
        cli.main(args)

        daemon.assert_not_called()
        real_main.assert_called_once_with(cli.parse_args(args))

    def test_daemonize_true(self, daemon, real_main):
        args = ["-d"]
        cli.main(args)

        daemon.assert_called_once_with()
        real_main.assert_called_once_with(cli.parse_args(args))


@mock.patch("larry.cli.asyncio.get_event_loop")
class RealMainTests(TestCase):
    def setUp(self):
        super().setUp()

        config = f"""\
[larry]
output = {self.tmpdir}/larry.svg
plugins = command
"""
        self.config_path = f"{self.tmpdir}/larry.cfg"
        with open(self.config_path, "w", encoding="UTF-8") as fp:
            fp.write(config)

    def test(self, get_event_loop):
        args = argparse.Namespace(
            config_path=self.config_path,
            debug=False,
            interval=60,
            list_filters=False,
            list_plugins=False,
        )

        cli.real_main(args)

        loop = get_event_loop.return_value
        loop.add_signal_handler.assert_called_once_with(
            signal.SIGUSR1, cli.run_every, args.interval, args.config_path, loop
        )
        loop.call_soon.assert_called_once_with(
            cli.run_every, args.interval, args.config_path, loop
        )
        loop.run_forever.assert_called_once_with()
        loop.close.assert_called_once_with()

    def test_with_interval_0(self, get_event_loop):
        args = argparse.Namespace(
            config_path=self.config_path,
            debug=False,
            interval=0,
            list_filters=False,
            list_plugins=False,
        )

        cli.real_main(args)

        loop = get_event_loop.return_value
        loop.add_signal_handler.assert_called_once_with(
            signal.SIGUSR1, cli.run, args.config_path
        )

    def test_keyboard_interrupt_stops_loop(self, get_event_loop):
        args = argparse.Namespace(
            config_path=self.config_path,
            debug=False,
            interval=60,
            list_filters=False,
            list_plugins=False,
        )
        loop = get_event_loop.return_value
        loop.run_forever.side_effect = KeyboardInterrupt()

        cli.real_main(args)

        loop.stop.assert_called_once_with()

    def test_list_plugins(self, get_event_loop):
        args = argparse.Namespace(
            config_path=self.config_path, debug=False, list_plugins=True
        )

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.real_main(args)

        self.assertIn("[X] command", stdout.getvalue())
        get_event_loop.assert_not_called()

    def test_list_filters(self, get_event_loop):
        args = argparse.Namespace(
            config_path=self.config_path,
            debug=False,
            list_plugins=False,
            list_filters=True,
        )

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.real_main(args)

        self.assertIn("[X] gradient", stdout.getvalue())
        get_event_loop.assert_not_called()

    @mock.patch("larry.cli.LOGGER")
    def test_with_debug(self, logger, _get_event_loop):
        args = argparse.Namespace(
            config_path=self.config_path, debug=True, list_plugins=True
        )

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.real_main(args)

        logger.setLevel.assert_called_once_with("DEBUG")
