from random import randint
from typing import TYPE_CHECKING, Any, TypedDict, cast

import jwt as jwt_lib
from pytest import mark, raises
from sqlalchemy import func, select

from shared.utils import to_fixed
from src.application.exceptions import ServiceException
from src.application.services import AuthService, StockService
from src.domain.models import Stock, User

from .conftest import BaseFixtures, default_password, stocks

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class RequestType(TypedDict):
    stock: str
    times: int


class TestAuthService(BaseFixtures):
    def is_valid_jwt(self, token: str):
        try:
            jwt_lib.decode(token, options={"verify_signature": False})  # type: ignore
            return True
        except jwt_lib.ExpiredSignatureError:
            return True
        except jwt_lib.DecodeError:
            return False
        except Exception:
            return False

    @mark.parametrize(argnames="is_superuser", argvalues=(True, False))
    async def test_create_user(
        self, auth_svc: AuthService, session: "AsyncSession", is_superuser: bool
    ):
        amount_of_users_before = await session.scalar(select(func.count(User.id)))
        user = await auth_svc.create(
            username="user", password=default_password, is_superuser=is_superuser
        )
        amount_of_users_after = await session.scalar(select(func.count(User.id)))

        assert not amount_of_users_before
        assert amount_of_users_after == 1
        assert user.id == 1
        assert user.username == "user"
        assert user.password != "user"
        assert user.is_superuser == is_superuser
        auth_svc._verify_password(raw="user", hashed=user.password)  # type: ignore

    async def test_create_user_should_raise_when_the_username_is_already_taken(
        self, auth_svc: AuthService, user: User
    ):
        EXPECTED_ERROR_MESSAGE = "Username is already taken"
        EXPECTED_ERROR_CODE = 400
        with raises(ServiceException) as exc_info:
            await auth_svc.create(
                username=user.username,
                password=default_password,
                is_superuser=user.is_superuser,
            )

        assert isinstance(exc_info.value, ServiceException)
        assert exc_info.value.message == EXPECTED_ERROR_MESSAGE
        assert exc_info.value.code == EXPECTED_ERROR_CODE

    async def test_login(self, auth_svc: AuthService, user: User):
        jwt = await auth_svc.login(username=user.username, password=default_password)
        assert self.is_valid_jwt(token=jwt)

    @mark.parametrize(
        argnames="username,password",
        argvalues=[("test", default_password), ("user", "test")],
    )
    async def test_login_should_raise_when_credentials_are_incorrect(
        self, auth_svc: AuthService, user: User, username: str, password: str
    ):
        EXPECTED_ERROR_MESSAGE = "Username or password are incorrect"
        EXPECTED_ERROR_CODE = 400
        with raises(ServiceException) as exc_info:
            await auth_svc.login(username=username, password=password)

        assert isinstance(exc_info.value, ServiceException)
        assert exc_info.value.message == EXPECTED_ERROR_MESSAGE
        assert exc_info.value.code == EXPECTED_ERROR_CODE

    async def test_authenticate(self, auth_svc: AuthService, user: User):
        jwt = await auth_svc.login(username=user.username, password=default_password)
        logged_user = await auth_svc.authenticate(token=jwt)

        assert logged_user.id == user.id
        assert logged_user.username == user.username
        assert logged_user.password == user.password
        assert logged_user.is_superuser == user.is_superuser

    async def test_authenticate_should_raise_when_an_invalid_token_is_set(
        self, auth_svc: AuthService
    ):
        EXPECTED_ERROR_MESSAGE = "Token is invalid"
        EXPECTED_ERROR_CODE = 401
        with raises(ServiceException) as exc_info:
            await auth_svc.authenticate(token="token")

        assert isinstance(exc_info.value, ServiceException)
        assert exc_info.value.message == EXPECTED_ERROR_MESSAGE
        assert exc_info.value.code == EXPECTED_ERROR_CODE

    async def test_authenticate_should_raise_when_user_authenticates_but_gets_deleted(
        self, auth_svc: AuthService, user: User, session: "AsyncSession"
    ):
        EXPECTED_ERROR_MESSAGE = "User not found"
        EXPECTED_ERROR_CODE = 404
        jwt = await auth_svc.login(username=user.username, password=default_password)

        await session.delete(user)
        await session.flush()

        with raises(ServiceException) as exc_info:
            await auth_svc.authenticate(token=jwt)

        assert isinstance(exc_info.value, ServiceException)
        assert exc_info.value.message == EXPECTED_ERROR_MESSAGE
        assert exc_info.value.code == EXPECTED_ERROR_CODE


class TestStockService(BaseFixtures):
    @mark.parametrize(
        argnames="stock,expected",
        argvalues=[
            (
                key,
                {
                    "symbol": stocks[key]["symbol"],
                    "company_name": stocks[key]["name"],
                    "quote": to_fixed(cast(float, stocks[key]["close"])),
                },
            )
            for key in stocks
        ],
    )
    async def test_get_stock_details(
        self,
        stock_svc: StockService,
        user: User,
        session: "AsyncSession",
        stock: str,
        expected: dict[str, Any],
    ):
        stocks_before = await session.scalar(
            select(func.count(Stock.id)).where(Stock.user_id == user.id)
        )
        stock_details = await stock_svc.get_stock_details(stock=stock, user=user)
        stocks_after = (
            await session.scalars(select(Stock).where(Stock.user_id == user.id))
        ).all()
        instance = stocks_after[0]

        assert not stocks_before
        assert len(stocks_after) == 1
        assert stock_details == expected
        assert instance.id == 1
        assert instance.symbol == expected["symbol"]
        assert instance.name == expected["company_name"]
        assert to_fixed(instance.close) == expected["quote"]
        assert instance.user_id == user.id

    async def test_get_stock_details_should_raise_when_proxy_is_none(
        self, stock_svc: StockService, user: User
    ):
        EXPECTED_ERROR_MESSAGE = "You need to pass a proxy adapter for this function"
        EXPECTED_ERROR_CODE = 500

        stock_svc.proxy = None
        with raises(ServiceException) as exc_info:
            await stock_svc.get_stock_details("A.US", user=user)

        assert isinstance(exc_info.value, ServiceException)
        assert exc_info.value.message == EXPECTED_ERROR_MESSAGE
        assert exc_info.value.code == EXPECTED_ERROR_CODE

    async def test_get_stock_details_should_raise_when_can_not_find_stock_data(
        self, stock_svc: StockService, user: User
    ):
        EXPECTED_ERROR_MESSAGE = (
            "Could not fetch the details for the stock. Try again later"
        )
        EXPECTED_ERROR_CODE = 424

        with raises(ServiceException) as exc_info:
            await stock_svc.get_stock_details("test", user=user)

        assert isinstance(exc_info.value, ServiceException)
        assert exc_info.value.message == EXPECTED_ERROR_MESSAGE
        assert exc_info.value.code == EXPECTED_ERROR_CODE

    @mark.parametrize(
        argnames="req",
        argvalues=[{"stock": key, "times": randint(2, 10)} for key in stocks],
    )
    async def test_get_history(
        self,
        stock_svc: StockService,
        user: User,
        req: RequestType,
        session: "AsyncSession",
    ):
        stock_data = stocks[req["stock"]]
        expected = {
            "date": stock_data["date"],
            "name": stock_data["name"],
            "symbol": stock_data["symbol"],
            "open": to_fixed(cast(float, stock_data["open"])),
            "high": to_fixed(cast(float, stock_data["high"])),
            "low": to_fixed(cast(float, stock_data["low"])),
            "close": to_fixed(cast(float, stock_data["close"])),
        }

        history_entries_before = await session.scalar(
            select(func.count(Stock.id)).where(Stock.user_id == user.id)
        )
        for _ in range(req["times"]):
            await stock_svc.get_stock_details(stock=req["stock"], user=user)
        history_entries_after = await session.scalar(
            select(func.count(Stock.id)).where(Stock.user_id == user.id)
        )

        history = await stock_svc.get_history(user=user)

        assert not history_entries_before
        assert history_entries_after == req["times"]
        assert len(history) == req["times"]
        for entry in history:
            assert entry == expected

    async def test_get_stats(
        self,
        stock_svc: StockService,
        user: User,
        superuser: User,
    ):
        expected_results: list[dict[str, str | int]] = []
        for stock in stocks:
            for _ in range(count := randint(2, 20)):
                await stock_svc.get_stock_details(stock=stock, user=user)
            expected_results.append({"stock": stock, "times_requested": count})

        expected_results.sort(key=lambda el: el["times_requested"], reverse=True)

        for result, expected in zip(
            await stock_svc.get_stats(user=superuser), expected_results
        ):
            assert result == expected

    async def test_get_stats_should_raise_when_user_is_not_superuser(
        self, stock_svc: StockService, user: User
    ):
        EXPECTED_ERROR_MESSAGE = "User is not allowed to access this service"
        EXPECTED_ERROR_CODE = 403

        with raises(ServiceException) as exc_info:
            await stock_svc.get_stats(user=user)

        assert isinstance(exc_info.value, ServiceException)
        assert exc_info.value.message == EXPECTED_ERROR_MESSAGE
        assert exc_info.value.code == EXPECTED_ERROR_CODE
