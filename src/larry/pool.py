"""Universal execution pool

Callers can run a function in a non async function in a thread and await the result
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar, TypeVarTuple

pool = ThreadPoolExecutor()


P = TypeVarTuple("P")
R = TypeVar("R")


async def run(func: Callable[[*P], R], *args: *P) -> R:
    """Apply the givne func/args to the executor pool and yield the result"""
    loop = asyncio.get_event_loop()

    return await loop.run_in_executor(pool, func, *args)
