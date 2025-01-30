from functools import wraps
from typing import Awaitable, Callable, Literal
from urllib.parse import urlencode

from anyio import sleep
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient, Response
from pydantic import BaseModel


class ResponseSchema(BaseModel):
    symbol: str
    date: str
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    name: str


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


app = FastAPI()


@app.get("/details/{stock}", response_model=ResponseSchema)
async def get_stock_details(stock: str):
    try:
        qs = {"s": stock, "f": "sd2t2ohlcvn", "e": "json"}
        response = await fetch(
            method="GET",
            url=f"https://stooq.com/q/l/?{urlencode(qs)}",
            expected_status_codes=(200,),
        )
        return response.json()["symbols"][0]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not complete the request to the third-party service. "
                "Check the logs"
            ),
        ) from exc
