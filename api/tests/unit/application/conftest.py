from datetime import datetime
from typing import TYPE_CHECKING, cast

from bcrypt import gensalt, hashpw
from pytest import fixture

from src.application.ports import ProxyPort, StockDetails
from src.application.services import AuthService, StockService
from src.domain.models import User
from src.infra.repository.stocks import StocksRepo
from src.infra.repository.users import UsersRepo

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


stocks: dict[str, dict[str, float | str]] = {
    "AAPL.US": {
        "close": 239.12,
        "date": "2025-01-28 19:03:58",
        "high": 240.19,
        "low": 230.81,
        "name": "APPLE",
        "open": 230.85,
        "symbol": "AAPL.US",
        "volume": 29605802,
    },
    "A.US": {
        "close": 150.96,
        "date": "2025-01-27 22:00:16",
        "high": 152.22,
        "low": 148.73,
        "name": "AGILENT TECHNOLOGIES",
        "open": 151.19,
        "symbol": "A.US",
        "volume": 2229590,
    },
    "ABEV.US": {
        "close": 1.85,
        "date": "2025-01-28 22:00:13",
        "high": 1.87,
        "low": 1.83,
        "name": "AMBEV",
        "open": 1.84,
        "symbol": "ABEV.US",
        "volume": 70520493,
    },
}

default_password = "password"


class BaseFixtures:
    @property
    def hashed_pwd(self):
        return hashpw(password=default_password.encode(), salt=gensalt()).decode()

    @fixture
    def auth_svc(self, session: "AsyncSession"):
        return AuthService(repo=UsersRepo(session=session))

    @fixture
    def stock_svc(self, session: "AsyncSession"):
        return StockService(stocks_repo=StocksRepo(session=session), proxy=ProxyMock())

    @fixture
    async def user(self, session: "AsyncSession"):
        instance = User(username="user", password=self.hashed_pwd)
        session.add(instance)
        await session.flush()
        return instance

    @fixture
    async def superuser(self, session: "AsyncSession"):
        instance = User(
            username="superuser", password=self.hashed_pwd, is_superuser=True
        )
        session.add(instance)
        await session.flush()
        return instance


class ProxyMock(ProxyPort):
    async def fetch_details_for_stock(self, stock: str):
        if stock not in stocks:
            return

        data = stocks[stock]
        return cast(
            StockDetails,
            {
                "symbol": data["symbol"],
                "name": data["name"],
                "stock_datetime": datetime.strptime(
                    cast(str, data["date"]), "%Y-%m-%d %H:%M:%S"
                ),
                "open": data["open"],
                "high": data["high"],
                "low": data["low"],
                "close": data["close"],
                "volume": data["volume"],
            },
        )
