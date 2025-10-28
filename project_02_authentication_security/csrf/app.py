import contextlib
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Form, HTTPException, Response, status
from fastapi.security import APIKeyCookie
from sqlalchemy import exc, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware
from starlette_csrf import CSRFMiddleware

from chapter07.csrf import schemas
from chapter07.csrf.authentication import authenticate, create_access_token
from chapter07.csrf.database import create_all_tables, get_async_session
from chapter07.csrf.models import AccessToken, User
from chapter07.csrf.password import get_password_hash

TOKEN_COOKIE_NAME = "token"
CSRF_TOKEN_SECRET = "__CHANGE_THIS_WITH_YOUR_OWN_SECRET_VALUE__"


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is a widely used pattern that works well to prevent such risks.
app.add_middleware(
    CSRFMiddleware,
    secret=CSRF_TOKEN_SECRET,
    sensitive_cookies={TOKEN_COOKIE_NAME},
    cookie_domain="localhost",
)

async def get_current_user(
    token: str = Depends(APIKeyCookie(name=TOKEN_COOKIE_NAME)), # `APIKeyCookie` allows us to retrieve the token from the cookie that was sent in the request.
    session: AsyncSession = Depends(get_async_session),
) -> User:
    query = select(AccessToken).where(
        AccessToken.access_token == token,
        AccessToken.expiration_date >= datetime.now(tz=timezone.utc),
    )
    result = await session.execute(query)
    access_token: AccessToken | None = result.scalar_one_or_none()

    if access_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return access_token.user


@app.get("/csrf")
async def csrf():
    return None

@app.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRead
)
async def register(
    user_create: schemas.UserCreate, session: AsyncSession = Depends(get_async_session)
) -> User:
    hashed_password = get_password_hash(user_create.password)
    user = User(
        **user_create.dict(exclude={"password"}), hashed_password=hashed_password
    )

    try:
        session.add(user)
        await session.commit()
    except exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    return user

@app.post("/login")
async def login(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
):
    user = await authenticate(email, password, session)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = await create_access_token(user, session)

    response.set_cookie(
        TOKEN_COOKIE_NAME,
        token.access_token,
        max_age=token.max_age(),
        secure=True, # value can't be read from JS
        httponly=True, # sent only over HTTPS
        # While this is not enough to prevent every kind of attack, it's crucial for such sensitive information. 
        samesite="lax", # this allows us to control how the cookie is sent in a cross-origin context. `lax` is the default value in most browsers and allows the cookie to be sent to subdomains of the cooke domain but prevents it for other sites. In a sense, it's designed to be the standard, built-in protection against CSRF.
    )

@app.get("/me", response_model=schemas.UserRead)
async def get_me(user: User = Depends(get_current_user)):
    return user

@app.post("/me", response_model=schemas.UserRead)
async def update_me(
    user_update: schemas.UserUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Update the email address of the authenticated user.
    """
    user_update_dict = user_update.dict(exclude_unset=True)
    for key, value in user_update_dict.items():
        setattr(user, key, value)

    session.add(user)
    await session.commit()

    return user