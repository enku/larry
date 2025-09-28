"""Tests for the universal thread pool"""

# pylint: disable=missing-docstring

from unittest import IsolatedAsyncioTestCase

from larry import pool


class RunTests(IsolatedAsyncioTestCase):
    async def test(self) -> None:
        def func(value):
            return value

        new_value = await pool.run(func, 9)

        self.assertEqual(new_value, 9)
