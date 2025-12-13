"""non-Color/Image types for larry"""

import asyncio

STOP_EVENT = asyncio.Event()


class Handler:
    """Process timer handle"""

    _handler = None

    @classmethod
    def get(cls) -> asyncio.TimerHandle | None:
        """Return the timer handle if one is set"""
        return cls._handler

    @classmethod
    def set(cls, handler: asyncio.TimerHandle | None) -> None:
        """Set the timer handle"""
        cls._handler = handler
