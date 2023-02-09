from sqlalchemy.orm import mapped_column, Mapped

from webspot.models.base import Base


class RequestModel(Base):
    __tablename__ = 'requests'

    id: Mapped[int] = mapped_column(primary_key=True)
    page_id: Mapped[int] = mapped_column(index=True)
    html: Mapped[str] = mapped_column(nullable=True)
    results: Mapped[str] = mapped_column(nullable=True)
    valid: Mapped[bool] = mapped_column(nullable=True)
