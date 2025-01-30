from dataclasses import dataclass
from functools import partial

from loguru import logger
from quart import Quart

from conf import settings
from src.application.ports import SqlDBPort
from src.infra.db import SqlDBAdapter

from .handlers import get_handlers
from .routers import get_routers


@dataclass
class State:
    db: SqlDBPort


class ASGIFactory:
    @classmethod
    def new(cls):
        return cls().application

    def __init__(self):
        self.application = Quart(__name__)
        self.application.state = State(db=SqlDBAdapter(settings.DATABASE_URL))  # type: ignore
        self._connected = False

        for error in (handlers := get_handlers()):
            self.application.errorhandler(error)(handlers[error])

        for router in get_routers():
            self.application.register_blueprint(router)

        self.application.before_serving(
            partial(self._on_startup, self.application.state)  # type: ignore
        )
        self.application.after_serving(
            partial(self._on_shutdown, self.application.state)  # type: ignore
        )

    async def _on_startup(self, state: State):
        if not self._connected:
            await state.db.connect()
            self._connected = True
            logger.info("Connected to the database")

    async def _on_shutdown(self, state: State):
        if self._connected:
            await state.db.disconnect()
            self._connected = False
            logger.info("Disconnected from the database")


app = ASGIFactory.new()
