from contextlib import asynccontextmanager
from functools import partial, wraps
from typing import Awaitable, Callable

import anyio
import uvicorn
from loguru import logger
from typer import Typer

from conf import settings
from src.application.services import AuthService
from src.infra.db import SqlDBAdapter
from src.infra.repository.users import UsersRepo


def coroutine[**Spec, T](func: Callable[Spec, Awaitable[T]]):
    @wraps(func)
    def wrapper(*args: Spec.args, **kwargs: Spec.kwargs):
        return anyio.run(func=partial(func, *args, **kwargs))

    return wrapper


@asynccontextmanager
async def start_session():
    db = SqlDBAdapter(connection_string=settings.DATABASE_URL)
    await db.connect()
    try:
        async with db.begin_session() as session:
            yield session
    finally:
        await db.disconnect()


app = Typer()


@app.command(name="createuser")
@coroutine
async def create_user(username: str, password: str, is_superuser: bool = False):
    async with start_session() as session:
        svc = AuthService(repo=UsersRepo(session=session))
        user = await svc.create(
            username=username, password=password, is_superuser=is_superuser
        )
        logger.info(f"User of id '{user.id}' created successfully!")


@app.command(name="login")
@coroutine
async def login(username: str, password: str):
    async with start_session() as session:
        svc = AuthService(repo=UsersRepo(session=session))
        token = await svc.login(username=username, password=password)
        logger.info(token)


@app.command("runserver")
def runserver():
    uvicorn.run(
        settings.ASGI_APP,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.should_reload,
    )
