import uvloop
from loguru import logger
from pytest import fixture

from conf import settings
from src.domain.models import BaseModel
from src.infra.db import SqlDBAdapter


@fixture(scope="session", autouse=True)
def event_loop_policy():
    return uvloop.EventLoopPolicy()


@fixture(scope="session", autouse=True)
async def db():
    db = SqlDBAdapter(connection_string=settings.DATABASE_URL)
    await db.connect()
    logger.info("Connected to the database")
    try:
        yield db
    finally:
        await db.disconnect()
        logger.info("Disconnected from the database")


@fixture(scope="session", autouse=True)
async def migrate(db: SqlDBAdapter):
    await db.migrate(base_model=BaseModel)
    logger.info("Migrated all the models for testing")


@fixture
async def session(db: SqlDBAdapter):
    async with db.begin_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
