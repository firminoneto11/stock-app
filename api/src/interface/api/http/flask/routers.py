from quart import Blueprint as Router

from conf import settings

from .controllers import router as stocks_router


def get_routers():
    v1_router = Router("v1", __name__, url_prefix=f"/{settings.API_PREFIX}/v1")
    v1_router.register_blueprint(stocks_router)
    return [v1_router]
