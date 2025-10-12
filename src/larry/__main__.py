"""larry.__main__"""

import asyncio

from larry import cli


def main():
    """script entry point"""
    loop = asyncio.get_event_loop()
    cli.run_loop(loop)


if __name__ == "__main__":
    main()
