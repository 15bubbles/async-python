import asyncio
import aiohttp
import aiofiles


BASE_URL = "https://jsonplaceholder.typicode.com/posts"
URLS = [f"{BASE_URL}/{i}" for i in range(0, 1000)]


async def get_url(session: aiohttp.ClientSession, url: str) -> str:
    response = await session.request("GET", url)
    data = await response.text()

    return data


async def write_to_file(filename: str, data: str):
    async with aiofiles.open(filename, mode="w") as file_handle:
        await file_handle.write(data)


async def request_and_write_results(
    session: aiohttp.ClientSession, url: str, filename: str
):
    data = await get_url(session, url)
    await write_to_file(filename, data)


def get_chunked_enumerated_urls(chunk_size=100):
    for i in range(0, len(URLS), chunk_size):
        yield [(i + idx, url) for idx, url in enumerate(URLS[i : i + chunk_size])]


async def main():
    async with aiohttp.ClientSession() as session:
        chunked_enumerated_urls = get_chunked_enumerated_urls()

        for chunk in chunked_enumerated_urls:
            tasks = [
                request_and_write_results(session, url, f"{i}.json") for i, url in chunk
            ]
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
