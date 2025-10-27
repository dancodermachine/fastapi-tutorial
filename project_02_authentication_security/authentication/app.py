import contextlib
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import exc, select
from sqlalchemy.ext.asyncio import AsyncSession

from project_02_authentication_security.authentication import schemas
from project_02_authentication_security.authentication.authentication import authenticate, create_access_token
from project_02_authentication_security.authentication.database import create_all_tables, get_async_session
from project_02_authentication_security.authentication.models import AccessToken, User
from project_02_authentication_security.authentication.password import get_password_hash


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    yield


app = FastAPI(lifespan=lifespan)


async def get_current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/token")), # Checks for the access token in the`Authorization` header. Gets fresh token.
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Retrieve a token from a request header, but then, we'll have to check the database to see whether it's valid. If it is, we'll return the corresponding user.
    """
    query = select(AccessToken).where(
        AccessToken.access_token == token,
        AccessToken.expiration_date >= datetime.now(tz=timezone.utc),
    )
    result = await session.execute(query)
    access_token: AccessToken | None = result.scalar_one_or_none()

    if access_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return access_token.user


@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRead)
async def register(user_create: schemas.UserCreate, session: AsyncSession = Depends(get_async_session)) -> User:
    # Hash the password before inserting into our database
    hashed_password = get_password_hash(user_create.password)
    user = User(**user_create.dict(exclude={"password"}), hashed_password=hashed_password)
    try:
        session.add(user)
        await session.commit()
    # Catching trying to insert an email that already exists.
    except exc.IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    return user


@app.post("/token")
async def create_token(
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    # We retrieve the request data thanks to the OAuth2PasswordRequestForm. It follows the OAuth2 protocol, which means you also have fields for the cleint ID and secret. 
    session: AsyncSession = Depends(get_async_session),
):
    """
    Login endpoint. Goal:
        1. Take credentials in the request payload.
        2. Retrieve the corresponding user.
        3. Check the password.
        4. Generate a new access token.
    """
    # Retrieve email
    email = form_data.username
    # Retrieve password
    password = form_data.password
    user = await authenticate(email, password, session)

    # If no corresponding user is found, we raise a 401 error.
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = await create_access_token(user, session)

    return {"access_token": token.access_token, "token_type": "bearer"}


@app.get("/protected-route", response_model=schemas.UserRead)
async def protected_route(user: User = Depends(get_current_user)):
    """
    Protect our endpoints simply by injecting this dependency
    """
    return user