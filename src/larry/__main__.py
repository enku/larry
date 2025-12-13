"""larry.__main__"""

import asyncio

from larry import cli


def main():
    """script entry point"""
    parser = cli.parser
    args = parser.parse_args()

    try:
        asyncio.run(cli.main(args))
    except KeyboardInterrupt:
        cli.LOGGER.info("User interrupted")
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            pass
        else:
            cli.STOP_EVENT.set()
            loop.stop()


if __name__ == "__main__":
    main()
