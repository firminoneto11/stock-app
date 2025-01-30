from dataclasses import dataclass
from datetime import datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports import StocksRepoPort, StockStat
from src.domain.models import Stock


@dataclass
class StocksRepo(StocksRepoPort):
    session: AsyncSession

    async def get_stocks_history(self, user_id: int):
        stmt = (
            select(Stock)
            .where(Stock.user_id == user_id)
            .order_by(Stock.created_at.desc())
        )
        return (await self.session.scalars(stmt)).all()

    async def get_most_requested_stocks(self, up_to: int = 5):
        stmt = (
            select(Stock.symbol, func.count(Stock.symbol).label("times"))
            .group_by(Stock.symbol)
            .order_by(func.count(Stock.symbol).desc())
            .limit(up_to)
        )

        result = (await self.session.execute(stmt)).all()
        data = cast(list[StockStat], [])

        for row in result:
            tpl = row._tuple()  # type: ignore
            stock, times = tpl[0], tpl[1]
            data.append({"stock": stock, "times_requested": times})

        return data

    async def create(
        self,
        symbol: str,
        name: str,
        stock_datetime: datetime,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: int,
        user_id: int,
    ):
        instance = Stock(
            symbol=symbol,
            name=name,
            stock_datetime=stock_datetime,
            open=open,
            high=high,
            low=low,
            close=close,
            volume=volume,
            user_id=user_id,
        )
        self.session.add(instance=instance)
        await self.session.flush()
        return instance
