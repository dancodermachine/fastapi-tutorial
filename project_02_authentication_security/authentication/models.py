
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def get_expiration_date(duration_seconds: int = 86400) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(seconds=duration_seconds)

def generate_token() -> str:
    return secrets.token_urlsafe(32)

class Base(DeclarativeBase):
    pass

class User(Base):
    """
    Creating the SQLAlchemy ORM model for a user.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(1024), index=True, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)


class AccessToken(Base):
    """
    We don't need Pydantic schemas here, as access tokens will be created and serialized through specific methods.
    """
    __tablename__ = "access_tokens"
    # `access_token`: This is the string that will be passed in the requests to authenticate them. Notice that we defined the `generate_token`` function as the default factory; it's a simple function defined previously that generates a random secure passphrase. Under the hood, it relies on the standard secrets module.
    access_token: Mapped[str] = mapped_column(String(1024), primary_key=True, default=generate_token)
    # `user_id`: A foreign key referring to the `users` table that identifies the user corresponding to this token.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # `expiration_date`: The date and time when the avvess token will expire and won't be valid anymore. It's always a good idea to give access tokens and expiry date to mitigate the risk if they are stolen. Default 24 hours. 
    expiration_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=get_expiration_date)

    user: Mapped[User] = relationship("User", lazy="joined")