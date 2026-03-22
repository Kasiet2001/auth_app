import enum
from sqlalchemy import Enum, Index, text
from sqlalchemy.orm import mapped_column, Mapped
from db.session import Base


class Role(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    role: Mapped[str] = mapped_column(Enum(Role), default=Role.USER)
    password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (
        Index(
            'users_email_active_index',
            'email',
            unique=True,
            postgresql_where=text("is_active = true")
        ),
    )