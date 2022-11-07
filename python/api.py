import asyncio
import collections
import time

import aiohttp
import fastapi

app = fastapi.FastAPI()


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


async def get_json_async(url: str) -> dict | list:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()


async def requests_async() -> tuple[float, dict]:
    start_time = time.time()

    todos = await todo_list_async()
    futures = [todo_details_async(todo["id"]) for todo in todos]
    value = await asyncio.gather(*futures)

    exec_time = time.time() - start_time
    return exec_time, count_todos(value)


async def requests_sync() -> tuple[float, dict]:
    start_time = time.time()

    todos = await todo_list_async()
    value = [await todo_details_async(todo["id"]) for todo in todos]

    exec_time = time.time() - start_time
    return exec_time, count_todos(value)


@app.get("/")
async def root():
    return {
        "async": await requests_async(),
        "sync": await requests_sync(),
    }


@app.get("/sync")
async def handler_sync():
    return {
        "results": await requests_sync(),
    }


@app.get("/async")
async def handler_async():
    return {
        "results": await requests_async(),
    }
