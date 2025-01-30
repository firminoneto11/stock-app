from datetime import datetime, timezone
from decimal import Decimal
from functools import lru_cache
from typing import Literal, overload

from environs import Env
from uuid_extensions import uuid7  # type: ignore


@lru_cache(maxsize=1)
def get_env():
    env = Env()
    env.read_env()
    return env


def generate_uuid(hexadecimal: bool = False):  # type: ignore
    uuid = uuid7()
    if hexadecimal:
        return uuid.hex  # type: ignore  # pragma: no cover
    return str(uuid)


@overload
def utc_timestamp(unix: Literal[True]) -> int: ...


@overload
def utc_timestamp(unix: Literal[False]) -> datetime: ...


def utc_timestamp(unix: bool = False):
    utc_now = datetime.now(tz=timezone.utc)
    if unix:
        utc_now = int(utc_now.timestamp())
    return utc_now


@overload
def to_fixed(
    n: float | Decimal, places: int = 2, as_float: Literal[True] = True
) -> float: ...


@overload
def to_fixed(
    n: float | Decimal, places: int, as_float: Literal[False] = False
) -> str: ...


def to_fixed(n: float | Decimal, places: int = 2, as_float: bool = True):
    fixed = f"{n:.{places}f}"
    return float(fixed) if as_float else fixed
