from sqlalchemy.orm import Mapped, mapped_column

from webspot.models.base import Base


class PageModel(Base):
    __tablename__ = 'pages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(index=True, unique=True)
