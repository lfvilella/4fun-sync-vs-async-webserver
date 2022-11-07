import asyncio
import random
import uuid

import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.future
import sqlalchemy.orm

Base = sqlalchemy.orm.declarative_base()
Session = sqlalchemy.orm.Session

_engine = sqlalchemy.ext.asyncio.create_async_engine(
    "sqlite+aiosqlite:///./local.db",
    echo=True,
)

_async_session_maker = sqlalchemy.orm.sessionmaker(
    _engine,
    expire_on_commit=False,
    class_=sqlalchemy.ext.asyncio.AsyncSession,
)


def create_session() -> Session:
    return _async_session_maker()


async def create_db_async():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Todo(Base):
    __tablename__ = "todos"

    id = sqlalchemy.Column(
        sqlalchemy.String(36),
        primary_key=True,
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    title = sqlalchemy.Column(sqlalchemy.String)
    completed = sqlalchemy.Column(
        sqlalchemy.SmallInteger,
        nullable=False,
        index=True,
    )


async def generate_random_todos(db_session: Session, total=3000):
    todos_to_be_added = [
        Todo(
            title=f"Title: {str(uuid.uuid4())}",
            completed=random.randint(0, 1),
        )
        for _ in range(total)
    ]
    db_session.add_all(todos_to_be_added)
    await db_session.commit()
    await db_session.flush()
    return todos_to_be_added


async def filter_todos(db_session: Session, limit: int) -> list:
    await asyncio.sleep(0.2)  # some latency to pull the data
    stmt = sqlalchemy.future.select(Todo).limit(limit)
    result = await db_session.execute(stmt)
    return result.fetchall()
