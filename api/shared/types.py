from typing import TYPE_CHECKING, Literal

from quart import Quart

if TYPE_CHECKING:
    from src.application.ports import SqlDBPort

type EnvChoices = Literal["development", "testing", "staging", "production"]


class _State:
    db: "SqlDBPort"


class ASGIApp(Quart):
    state: _State
