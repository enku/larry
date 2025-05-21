"""fixtures for larry tests"""

# pylint: disable=missing-docstring
import random as stdlib_random
import tempfile
from unittest import mock

import numpy as np
from unittest_fixtures import FixtureContext, Fixtures, fixture

from larry import config as larry_config


class ConfigMaker:
    def __init__(self, dirname: str) -> None:
        self.path = f"{dirname}/larry.cfg"
        self._section = "larry"
        self.config = larry_config.load(self.path)
        self.add_config(output=f"{dirname}/larry.svg")

    def add_config(self, **kwargs):
        for name, value in kwargs.items():
            self.config[self._section][name] = str(value)

        self._dump()

    def add_section(self, name: str):
        self.config.add_section(name)
        self._section = name
        self._dump()

    def _dump(self):
        with open(self.path, "w", encoding="UTF-8") as fp:
            self.config.write(fp)


@fixture()
def random(
    _fixtures: Fixtures, target="larry.color.random", seed: int = 1
) -> FixtureContext[stdlib_random.Random]:
    _random = stdlib_random.Random(seed)
    with mock.patch(target, new=_random):
        yield _random


@fixture()
def nprandom(_fixtures: Fixtures, seed: int = 1) -> FixtureContext[None]:
    original_state = np.random.get_state()

    np.random.seed(seed)
    yield None
    np.random.set_state(original_state)


@fixture()
def tmpdir(_fixtures: Fixtures) -> FixtureContext[str]:
    with tempfile.TemporaryDirectory() as tempdir:
        yield tempdir


@fixture("tmpdir")
def configmaker(fixtures: Fixtures) -> ConfigMaker:
    return ConfigMaker(fixtures.tmpdir)
