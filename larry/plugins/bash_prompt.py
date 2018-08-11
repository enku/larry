"""Larry Plugin to create my bash prompt colors"""
import os
from typing import List

from larry import LOGGER, Color, ConfigType, write_file


def plugin(colors: List[Color], config: ConfigType) -> None:
    """bash prompt plugin for larry"""
    LOGGER.debug('bash_prompt plugin begin')

    outfile = config.get('location', '~/.larry')
    outfile = os.path.expanduser(outfile)
    LOGGER.debug('writing colors out to %s', outfile)

    bash = ('exit_status=$?\n'
            'BASH_PROMPT_COLORS[color]=$(fgc {})\n'
            'BASH_PROMPT_COLORS[bgcolor]=$(bgc {})\n'
            'return ${{exit_status}}\n').format(
                str(colors[-1])[1:], str(colors[0])[1:])

    write_file(outfile, bash)
