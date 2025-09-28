"""Universal execution pool

Callers can run a function in a non async function in a thread and await the result
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor

pool = ThreadPoolExecutor()


async def run(func, *args):
    """Apply the givne func/args to the executor pool and yield the result"""
    loop = asyncio.get_event_loop()

    return await loop.run_in_executor(pool, func, *args)
