from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import TimeStampedBaseModel

if TYPE_CHECKING:
    from .users import User


class Stock(TimeStampedBaseModel):
    __tablename__ = "stocks"

    symbol: Mapped[str] = mapped_column(sa.String(10))
    name: Mapped[str] = mapped_column(sa.String(30))
    stock_datetime: Mapped[datetime] = mapped_column(sa.DateTime)

    open: Mapped[Decimal] = mapped_column(
        sa.Numeric(precision=15, scale=5, asdecimal=True)
    )
    high: Mapped[Decimal] = mapped_column(
        sa.Numeric(precision=15, scale=5, asdecimal=True)
    )
    low: Mapped[Decimal] = mapped_column(
        sa.Numeric(precision=15, scale=5, asdecimal=True)
    )
    close: Mapped[Decimal] = mapped_column(
        sa.Numeric(precision=15, scale=5, asdecimal=True)
    )
    volume: Mapped[int] = mapped_column(sa.Integer)

    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    user: Mapped["User"] = relationship(back_populates="stocks")
