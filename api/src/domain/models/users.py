from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import TimeStampedBaseModel

if TYPE_CHECKING:
    from .stocks import Stock


class User(TimeStampedBaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(sa.String(100), unique=True, index=True)
    password: Mapped[str] = mapped_column(sa.String)
    is_superuser: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    stocks: Mapped[list["Stock"]] = relationship(
        back_populates="user", order_by="Stock.created_at.desc()"
    )
