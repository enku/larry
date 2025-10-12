"""larry.__main__"""

import asyncio

from larry import cli


def main():
    """script entry point"""
    if (args := cli.main()) is None:
        return

    loop = asyncio.get_event_loop()
    loop.create_task(cli.async_main(args))
    cli.run_loop(loop)


if __name__ == "__main__":
    main()
