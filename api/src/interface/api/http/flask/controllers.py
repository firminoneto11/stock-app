from functools import wraps
from typing import TYPE_CHECKING, Awaitable, Callable, cast

from quart import Blueprint as Router
from quart import current_app, request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.types import ASGIApp
from src.application.exceptions import ServiceException
from src.application.services import AuthService, StockService
from src.infra.proxy import ProxyAdapter
from src.infra.repository.stocks import StocksRepo
from src.infra.repository.users import UsersRepo

if TYPE_CHECKING:
    from src.domain.models import User


router = Router("stocks", __name__)


def login_required[T](func: Callable[[AsyncSession, "User"], Awaitable[T]]):
    @wraps(func)
    async def wrapper[**Spec](*args: Spec.args, **kwargs: Spec.kwargs) -> T:
        app = cast(ASGIApp, current_app)
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        async with app.state.db.begin_session() as ses:  # type: ignore
            session = cast(AsyncSession, ses)
            svc = AuthService(repo=UsersRepo(session=session))

            try:
                user = await svc.authenticate(token=token)
            except ServiceException as exc:
                return cast(T, ({"detail": exc.message}, exc.code))

            return await func(session, user, *args, **kwargs)

    return wrapper


@router.get("/stock")
@login_required
async def get_stock_details(session: AsyncSession, user: "User"):
    if not (stock := request.args.get("q")):
        return {"detail": "The 'q' query param must be set"}, 400

    svc = StockService(proxy=ProxyAdapter(), stocks_repo=StocksRepo(session=session))

    if details := await svc.get_stock_details(stock=stock, user=user):
        return details, 200

    return {"detail": "No details found for this stock"}, 404


@router.get("/history")
@login_required
async def get_history(session: AsyncSession, user: "User"):
    svc = StockService(stocks_repo=StocksRepo(session=session))

    if history := await svc.get_history(user=user):
        return history, 200

    return {"detail": "No history found for this user"}, 404


@router.get("/stats")
@login_required
async def get_stats(session: AsyncSession, user: "User"):
    svc = StockService(stocks_repo=StocksRepo(session=session))

    if stats := await svc.get_stats(user=user):
        return stats, 200

    return {"detail": "No stats are currently available"}, 404
