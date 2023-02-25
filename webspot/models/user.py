from sqlalchemy.orm import mapped_column, Mapped

from webspot.models.base import Base


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
