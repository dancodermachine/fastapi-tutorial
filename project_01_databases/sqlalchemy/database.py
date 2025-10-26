from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from chapter06.sqlalchemy.models import Base

# sqlite -> database engine
# aiosqlite -> driver
# The hostname of the database server
DATABASE_URL = "sqlite+aiosqlite:///sqlalchemy.db"
# Create an engine using the create_async_engine
engine = create_async_engine(DATABASE_URL)
# Returns a function so that we can generate sessions tied to our database engine. A session will establish an actual connection with the database and represent a zone where it'll store all the objects you've read from the database and all the ones you've defined that'll be written to the database. It's the proxy between the ORM concepts and the fundamental SQL queries. When building HTTP servers, we usually open a fresh session when the request starts and close it when we answered the request. Therefore, each HTTP request represents a unit of work with the database.
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    This function works as context manager. It takes care of opening a connection to the database.
    """
    async with async_session_maker() as session:
        # Using yield ensures that the session remains open until the end of the request. It ensures we only get out of the context manager when the request and our endpoint logic have been fully handled by FastAPI.
        yield session


async def create_all_tables():
    """
    Creates the table's schema inside our database. If we don't do that, our database will be empty and we wouldn't be able to save or retrieve data.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)