from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __table_args__ = {'sqlite_autoincrement': True}

    created_at: Mapped[str] = mapped_column(default=lambda _: datetime.now().timestamp())
    created_by: Mapped[int] = mapped_column(index=True)
    updated_at: Mapped[str] = mapped_column(default=lambda _: datetime.now().timestamp())
    updated_by: Mapped[int] = mapped_column(index=True)
