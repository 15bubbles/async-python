import asyncio
from asyncio.queues import Queue
from typing import (
    AsyncGenerator,
    Awaitable,
    Callable,
    Iterable,
    Tuple,
    TypeVar,
)

import aiofiles
import aiohttp


# CONSTANTS

MAX_WORKERS = 50

BASE_URL = "https://jsonplaceholder.typicode.com/posts"
URLS = [f"{BASE_URL}/{i}" for i in range(0, 1000)]


# MAIN REQUEST MAKING AND FILE WRITING LOGIC


async def get_url(session: aiohttp.ClientSession, url: str) -> str:
    response = await session.request("GET", url)
    data = await response.text()

    return data


async def write_to_file(filename: str, data: str) -> None:
    async with aiofiles.open(filename, mode="w") as file_handle:
        await file_handle.write(data)


async def request_and_write_results(
    session: aiohttp.ClientSession, url: str, filename: str
) -> None:
    data = await get_url(session, url)
    await write_to_file(filename, data)


# HELPER FUNCTIONS

_IterableItem = TypeVar("_IterableItem")


async def async_enumerate(
    urls: Iterable[_IterableItem],
) -> AsyncGenerator[Tuple[int, _IterableItem], None]:
    for idx, url in enumerate(urls):
        yield idx, url


async def queued_worker_wrapper(
    coroutine_function: Callable[[aiohttp.ClientSession, str, str], Awaitable],
    session: aiohttp.ClientSession,
    queue: Queue,
) -> None:
    while True:
        print("Getting item from queue")
        url, filename = await queue.get()
        print(f"Got {url}, {filename} from queue")
        print(f"Running coroutine for {url}, {filename}")
        await coroutine_function(session, url, filename)
        print(f"Coruoutine finished for {url}, {filename}")
        print("Letting queue know that the task is done")
        queue.task_done()


# MAIN FUNCTION


async def main():
    queue = Queue(MAX_WORKERS)

    async with aiohttp.ClientSession() as session:
        workers = [
            asyncio.create_task(
                queued_worker_wrapper(request_and_write_results, session, queue)
            )
            for _ in range(MAX_WORKERS)
        ]

        async for idx, url in async_enumerate(URLS):
            filename = f"{idx}.txt"
            queue_item = (url, filename)
            await queue.put((url, filename))
            print(f"Item {queue_item} added into the queue")

        await queue.join()
        print("Queue joined")

    for worker in workers:
        worker.cancel()


if __name__ == "__main__":
    asyncio.run(main())
