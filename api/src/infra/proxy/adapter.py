from datetime import datetime
from functools import wraps
from typing import Awaitable, Callable, Literal, cast

from anyio import sleep
from httpx import AsyncClient, Response

from conf import settings
from src.application.ports import ProxyPort, StockDetails


class FetchException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def retry(times: int, delay: int):
    def _retry[**Spec, T](func: Callable[Spec, Awaitable[T]]):
        @wraps(func)
        async def actual_decorator(*args: Spec.args, **kwargs: Spec.kwargs) -> T:
            if times <= 0:
                return await func(*args, **kwargs)

            backoff, err = delay, None
            for idx in range(times):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    err = exc
                    if idx + 1 == times:
                        break

                    if backoff <= 0:
                        continue

                    await sleep(backoff)
                    backoff = backoff * 2

            msg = FetchException(message="Exhausted all of the retries")
            if err:
                raise msg from err
            raise msg

        return actual_decorator

    return _retry


@retry(times=2, delay=1)
async def fetch(
    method: Literal["GET"], url: str, expected_status_codes: tuple[int, ...]
):
    async with AsyncClient() as client:
        func: Callable[[str], Awaitable[Response]] = getattr(
            client, method.lower().strip()
        )

        response = await func(url)

    if response.status_code in expected_status_codes:
        return response

    raise FetchException(
        message="The external service returned an unexpected status code"
    )


class ProxyAdapter(ProxyPort):
    API_URL = settings.PROXY_URl

    async def fetch_details_for_stock(self, stock: str):
        response, err = await self._make_request(
            method="GET", endpoint=f"details/{stock}"
        )

        if err:
            return

        details = response.json()

        return cast(
            StockDetails,
            {
                "symbol": details["symbol"],
                "name": details["name"],
                "stock_datetime": datetime.strptime(
                    f"{details['date']} {details['time']}", "%Y-%m-%d %H:%M:%S"
                ),
                "open": details["open"],
                "high": details["high"],
                "low": details["low"],
                "close": details["close"],
                "volume": details["volume"],
            },
        )

    async def _make_request(
        self,
        method: Literal["GET"],
        endpoint: str,
        expected_status_codes: tuple[int, ...] = (200,),
    ):
        url = f"{self.API_URL}/{endpoint}"

        try:
            response = await fetch(
                method=method, url=url, expected_status_codes=expected_status_codes
            )
        except Exception as exc:
            return cast(Response, None), exc

        return response, None
