from dataclasses import dataclass
from datetime import timedelta
from math import floor
from typing import TYPE_CHECKING, Any, Optional, TypedDict, cast

import jwt
from bcrypt import checkpw, gensalt, hashpw

from conf import settings
from shared.utils import to_fixed, utc_timestamp

from .exceptions import JWTError, ServiceException
from .ports import ProxyPort, StocksRepoPort, UsersRepoPort

if TYPE_CHECKING:
    from src.domain.models import User

    class Payload(TypedDict):
        sub: str
        iat: int
        exp: int


@dataclass
class AuthService:
    repo: UsersRepoPort

    async def create(self, username: str, password: str, is_superuser: bool = False):
        if (await self.repo.get_by_username(username=username)) is not None:
            raise ServiceException(message="Username is already taken", code=400)

        return await self.repo.create(
            username=username,
            hashed_password=self._hash_password(raw=password),
            is_superuser=is_superuser,
        )

    async def login(self, username: str, password: str):
        if (user := await self.repo.get_by_username(username=username)) is None:
            raise ServiceException(
                message="Username or password are incorrect", code=400
            )

        if not self._verify_password(raw=password, hashed=user.password):
            raise ServiceException(
                message="Username or password are incorrect", code=400
            )

        return self._generate_jwt(uuid=user.uuid)

    async def authenticate(self, token: str):
        try:
            payload = self._validate_jwt(token=token)
        except JWTError as exc:
            raise ServiceException(message=exc.message, code=401)

        if (user := await self.repo.get_by_id(payload["sub"])) is None:
            raise ServiceException(message="User not found", code=404)

        return user

    def _generate_jwt(self, uuid: str):
        payload = {
            "sub": uuid,
            "iat": utc_timestamp(unix=True),
            "exp": floor(
                (
                    utc_timestamp(unix=False)
                    + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
                ).timestamp()
            ),
        }

        return jwt.encode(  # type: ignore
            payload=payload,
            key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_HASH_ALGO,
        )

    def _validate_jwt(self, token: str):
        try:
            return cast(
                "Payload",
                jwt.decode(  # type: ignore
                    jwt=token,
                    key=settings.JWT_SECRET_KEY,
                    algorithms=[settings.JWT_HASH_ALGO],
                ),
            )
        except jwt.ExpiredSignatureError:
            raise JWTError(message="Token has expired")  # pragma: no cover
        except jwt.InvalidTokenError:
            raise JWTError(message="Token is invalid")

    def _hash_password(self, raw: str):
        return hashpw(password=raw.encode(), salt=gensalt()).decode()

    def _verify_password(self, raw: str, hashed: str):
        return checkpw(password=raw.encode(), hashed_password=hashed.encode())


@dataclass
class StockService:
    stocks_repo: StocksRepoPort
    proxy: Optional[ProxyPort] = None

    async def get_stock_details(self, stock: str, user: "User"):
        if self.proxy is None:
            raise ServiceException(
                message="You need to pass a proxy adapter for this function", code=500
            )

        if (details := await self.proxy.fetch_details_for_stock(stock=stock)) is None:
            raise ServiceException(
                message="Could not fetch the details for the stock. Try again later",
                code=424,
            )

        instance = await self.stocks_repo.create(**details, user_id=user.id)

        return {
            "symbol": instance.symbol,
            "company_name": instance.name,
            "quote": to_fixed(instance.close),
        }

    async def get_history(self, user: "User"):
        data = cast(list[dict[str, Any]], [])
        if history := await self.stocks_repo.get_stocks_history(user_id=user.id):
            for entry in history:
                data.append(
                    {
                        "date": entry.stock_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        "name": entry.name,
                        "symbol": entry.symbol,
                        "open": to_fixed(entry.open),
                        "high": to_fixed(entry.high),
                        "low": to_fixed(entry.low),
                        "close": to_fixed(entry.close),
                    }
                )
        return data

    async def get_stats(self, user: "User"):
        if not user.is_superuser:
            raise ServiceException(
                message="User is not allowed to access this service", code=403
            )
        return await self.stocks_repo.get_most_requested_stocks(up_to=5)
