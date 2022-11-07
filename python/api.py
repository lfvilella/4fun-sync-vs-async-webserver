import asyncio
import time

import fastapi

import services_db
import services_http

app = fastapi.FastAPI()


async def get_db_session() -> services_db.Session:
    async with services_db.create_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def requests_async() -> tuple[float, dict]:
    start_time = time.time()

    todos = await services_http.todo_list_async()
    futures = [services_http.todo_details_async(todo["id"]) for todo in todos]
    value = await asyncio.gather(*futures)  # wait for all futures to resolve

    exec_time = time.time() - start_time
    return exec_time, services_http.count_todos(value)


async def requests_sync() -> tuple[float, dict]:
    start_time = time.time()

    todos = await services_http.todo_list_async()
    value = [
        await services_http.todo_details_async(todo["id"]) for todo in todos
    ]

    exec_time = time.time() - start_time
    return exec_time, services_http.count_todos(value)


async def db_filter_async(
    db_session: services_db.Session,
) -> tuple[float, list]:

    start_time = time.time()

    futures = []
    for limit in range(30):
        futures.append(services_db.filter_todos(db_session, limit))

    results = await asyncio.gather(*futures)  # wait for all futures to resolve

    exec_time = time.time() - start_time
    return exec_time, results


async def db_filter_sync(
    db_session: services_db.Session,
) -> tuple[float, list]:

    start_time = time.time()

    results = []
    for limit in range(30):
        todos = await services_db.filter_todos(db_session, limit)
        results.append(todos)

    exec_time = time.time() - start_time
    return exec_time, results


@app.get("/http-sync")
async def handler_sync():
    return {
        "results": await requests_sync(),
    }


@app.get("/http-async")
async def handler_async():
    return {
        "results": await requests_async(),
    }


@app.get("/db-create")
async def db_create_async(
    db_session: services_db.Session = fastapi.Depends(get_db_session),
):
    await services_db.create_db_async()
    todos = await services_db.generate_random_todos(db_session)
    return todos


@app.get("/db-async")
async def db_async(
    db_session: services_db.Session = fastapi.Depends(get_db_session),
):
    await services_db.create_db_async()
    return {
        "results": await db_filter_async(db_session),
    }


@app.get("/db-sync")
async def db_sync(
    db_session: services_db.Session = fastapi.Depends(get_db_session),
):
    await services_db.create_db_async()
    return {
        "results": await db_filter_sync(db_session),
    }


@app.get("/")
async def root(
    db_session: services_db.Session = fastapi.Depends(get_db_session),
):
    await services_db.create_db_async()
    await services_db.generate_random_todos(db_session)

    return {
        "http://localhost:8000/http-sync": (await requests_sync())[0],
        "http://localhost:8000/http-async": (await requests_async())[0],
        "http://localhost:8000/db-sync": (await db_filter_sync(db_session))[0],
        "http://localhost:8000/db-async": (await db_filter_async(db_session))[
            0
        ],
    }
