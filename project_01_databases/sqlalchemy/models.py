from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """
    Class inherits from DeclarativeBase. All our models will inherit from this class. SQLAlchemy uses it to keep all the information about your database schema together. This is why you should create it only once in your whole project and always use the same one throughout.
    """
    pass

class Post(Base):
    """
    mapped_column helps us define the type of the column and its related properties. For example, we define our id column as an integer primary key with auto-increment.
    """
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)