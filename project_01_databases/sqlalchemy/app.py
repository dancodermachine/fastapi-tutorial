import contextlib
from collections.abc import Sequence

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from project_01_databases.sqlalchemy import schemas
from project_01_databases.sqlalchemy.database import create_all_tables, get_async_session
from project_01_databases.sqlalchemy.models import Post

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    yield

app = FastAPI(lifespan=lifespan)

async def pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
) -> tuple[int, int]:
    capped_limit = min(100, limit)
    return (skip, capped_limit)

async def get_post_or_404(
    id: int, session: AsyncSession = Depends(get_async_session)
) -> Post:
    select_query = select(Post).where(Post.id == id)
    result = await session.execute(select_query)
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return post

@app.get("/posts", response_model=list[schemas.PostRead]) 
async def list_posts(
    pagination: tuple[int, int] = Depends(pagination),
    session: AsyncSession = Depends(get_async_session), 
) -> Sequence[Post]:
    """
    List objects.
    """
    skip, limit = pagination
    # The `select` function of SQLAlchemy allows us to begin defining a query. Conveniently, we can directly pass it the `model` class: it'll automatically understand which table we are talking about. From there, we can apply various methods and filters, which are a mirror of what we could expect in a pure SQL.
    select_query = select(Post).offset(skip).limit(limit)
    # Since we read data from the database, it's an async operation.
    result = await session.execute(select_query)
    # We get a result object. This object is an instance of the Result class of SQLAlchemy. It's not directly our list of posts, but rather a set representing the results of the SQL query. That's why we need to call `scalars` and `all`. The first one will make sure we get the actual `Post` objects, while the second will return them as a sequence.
    return result.scalars().all()

@app.get("/posts/{id}", response_model=schemas.PostRead)
async def get_post(post: Post = Depends(get_post_or_404)) -> Post:
    """
    Get a specific object. It expects an ID.
    """
    return post

@app.post("/posts", response_model=schemas.PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(post_create: schemas.PostCreate, session: AsyncSession = Depends(get_async_session)) -> Post:
    # We inject a fresh SQLAlchemy session using our get_async_session dependency
    """
    Inserting new objects inside our database.
    The main challenge is to take a Pydantic schema as input, transform it into a SQLAlchemy model, and save it in the database. 
    """
    post = Post(**post_create.dict())
    # Post is in the session memory, but not in the database yet.
    session.add(post)
    # Commit method tells the session to generate the appropriate SQL queries and execute them on the database. We need to use await because we perform an I/O operation on the database, so it's an async operation.
    await session.commit()

    return post

@app.patch("/posts/{id}", response_model=schemas.PostRead)
async def update_post(
    post_update: schemas.PostPartialUpdate,
    post: Post = Depends(get_post_or_404),
    session: AsyncSession = Depends(get_async_session),
) -> Post:
    """
    Update post. We'll operate directly on the post we want to modify. When working with ORM, entities are objects that can be modified as you wish.
    """
    post_update_dict = post_update.dict(exclude_unset=True)
    for key, value in post_update_dict.items():
        setattr(post, key, value)

    session.add(post)
    await session.commit()

    return post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post: Post = Depends(get_post_or_404), session: AsyncSession = Depends(get_async_session)):
    await session.delete(post)
    await session.commit()