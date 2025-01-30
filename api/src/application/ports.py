from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from datetime import datetime
from typing import TYPE_CHECKING, AsyncContextManager, Sequence, TypedDict

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import DeclarativeBase

    from src.domain.models import Stock, User


class StockStat(TypedDict):
    stock: str
    times_requested: int


class StockDetails(TypedDict):
    symbol: str
    name: str
    stock_datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class SqlDBPort(metaclass=ABCMeta):
    @abstractmethod
    async def connect(
        self, echo_sql: bool = False, pool_size: int = 5, max_overflow: int = 5
    ) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    @asynccontextmanager  # type: ignore
    async def begin_session(self) -> AsyncContextManager["AsyncSession"]: ...

    @abstractmethod
    async def ping(self) -> None: ...

    @abstractmethod
    async def migrate(
        self, base_model: "type[DeclarativeBase]", drop: bool = False
    ) -> None: ...


class UsersRepoPort(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, session: "AsyncSession") -> None: ...

    @abstractmethod
    async def get_by_id(self, id: int | str) -> "User | None": ...

    @abstractmethod
    async def get_by_username(self, username: str) -> "User | None": ...

    @abstractmethod
    async def create(
        self, username: str, hashed_password: str, is_superuser: bool
    ) -> "User": ...


class StocksRepoPort(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, session: "AsyncSession") -> None: ...

    @abstractmethod
    async def get_stocks_history(self, user_id: int) -> Sequence["Stock"]: ...

    @abstractmethod
    async def get_most_requested_stocks(self, up_to: int = 5) -> list[StockStat]: ...

    @abstractmethod
    async def create(
        self,
        symbol: str,
        name: str,
        stock_datetime: datetime,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: int,
        user_id: int,
    ) -> "Stock": ...


class ProxyPort(metaclass=ABCMeta):
    @abstractmethod
    async def fetch_details_for_stock(self, stock: str) -> StockDetails | None: ...
