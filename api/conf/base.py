import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from shared.types import EnvChoices
from shared.utils import get_env

with open("pyproject.toml", mode="rb") as stream:
    pyproject: dict[str, str] = tomllib.load(stream)["project"]


ENV_PREFIX = "STOCK_API_"


with get_env().prefixed(ENV_PREFIX) as env:

    class BaseSettings:
        BASE_DIR = Path(__file__).parent.parent

        ENVIRONMENT_PREFIX = ENV_PREFIX

        APP_NAME = pyproject["name"]
        APP_DESCRIPTION = pyproject["description"]
        APP_VERSION = pyproject["version"]

        API_PREFIX = "/api"

        JWT_SECRET_KEY = env.str("JWT_SECRET_KEY")
        JWT_HASH_ALGO = env.str("JWT_HASH_ALGO")
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # A day

        PROXY_URl = env.str("PROXY_URL", "http://localhost:8001")

        ASGI_APP = "src.interface.api.http.flask.asgi:app"

        if TYPE_CHECKING:
            ENVIRONMENT: "EnvChoices"
            DATABASE_URL: str
            DEBUG: bool
            HOST: str
            PORT: int

        @property
        def autocommit(self):
            return self.ENVIRONMENT != "testing"

        @property
        def should_reload(self):
            return self.ENVIRONMENT == "development"  # pragma: no cover
