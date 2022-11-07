import collections

import aiohttp


async def get_json_async(url: str) -> dict | list:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()


async def todo_list_async() -> list:
    return await get_json_async("https://jsonplaceholder.typicode.com/todos")


async def todo_details_async(id: str) -> dict:
    detail = await get_json_async(
        f"https://jsonplaceholder.typicode.com/todos/{id}"
    )
    return detail


def count_todos(todos: list[dict]) -> dict:
    count = collections.defaultdict(int)
    for t in todos:
        count[f"completed_{t['completed']}".upper()] += 1

    return count
