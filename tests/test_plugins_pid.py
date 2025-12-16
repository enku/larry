"""Tests for the "pid" plugin"""

# pylint: disable=missing-docstring

import os
from unittest import IsolatedAsyncioTestCase

from unittest_fixtures import Fixtures, given

from larry.plugins import do_plugin

from . import lib


@given(lib.tmpdir)
class PID(IsolatedAsyncioTestCase):
    async def test(self, fixtures: Fixtures) -> None:
        tmpdir: str = fixtures.tmpdir
        config_path = f"{tmpdir}/larry.cfg"
        output = f"{tmpdir}/larry.pid"
        config = f"[plugins:pid]\noutput={output}\n"

        with open(config_path, "w", encoding="utf8") as fp:
            fp.write(config)

        await do_plugin("pid", [], config_path)

        pid = os.getpid()

        with open(output, "r", encoding="utf8") as fp:
            self.assertEqual(str(pid), fp.read())
