# Testing
In software development, a significant part of the developer's work should be dedicated to writing tests.
Unit tests, integration tests, end-to-end tests, acceptance tests, and others are techniques aim to validate the functionality of software from a micro level, where we test single functions (unit tests), to a macro level, where we test a global feature that delivers value to the user (acceptance tests).

This will save you time in the long run: first of all, tests can be run automatically in a few seconds, ensuring that all your software works, without you needing to manually go over every feature. Secondly, when you introduce new features or refactor the code, you're ensuring that you don't introduce bugs to existing parts of the software.

`pip install pytest`

In `pytest`, the only constraint to making it work is that the function name has to start with `test_` 
```python
from chapter09.chapter09_introduction import add

def test_add():
    assert add(2, 3) == 5
```
`Pytest` provides the `parametrize` marker. In `pytest`, a **marker** is a special decorator that's used to easily pass metadata to the test. Here, **parametrize** allows us to define several sets of variables that will be passed as arguments to the test function. **Parametrize** is a very convenient way to test different outcomes when it's given a different set of parameters.
```python
import pytest
from chapter09.chapter09_introduction import add
@pytest.mark.parametrize("a,b,result", [(2, 3, 5), (0, 0, 0), (100, 0, 100), (1, 1, 2)])
def test_add(a, b, result):
    assert add(a, b) == result
```
Fixtures are *simple functions* decorated *with the fixture decorator*. Inside, you can write any logic and return the object you'll need in your tests.  
```python
from datetime import date
from enum import Enum
from pydantic import BaseModel
import pytest

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    NON_BINARY = "NON_BINARY"

class Address(BaseModel):
    street_address: str
    postal_code: str
    city: str
    country: str

class Person(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    birthdate: date
    interests: list[str]
    address: Address

@pytest.fixture
def address():
    return Address(
        street_address="12 Squirell Street",
        postal_code="424242",
        city="Woodtown",
        country="US",
    )

@pytest.fixture
def person(address):
    return Person(
        first_name="John",
        last_name="Doe",
        gender=Gender.MALE,
        birthdate="1991-01-01",
        interests=["travel", "sports"],
        address=address,
    )

def test_address_country(address):
    """
    By setting an `address` argument on the test function, pytest automatically detects that it corresponds to the `address` fixture, executes it, and passes its return value.
    """
    assert address.country == "US"


def test_person_first_name(person):
    assert person.first_name == "John"


def test_person_address_city(person):
    assert person.address.city == "Woodtown"
```

## Tests for Rest API Endpoints
`HTTPX`, an `HTTP` client, allows us to have a pure asynchronous HTTP client able to make requests to our FastAPI app.

`pip install httpx asgi-lifespan pytest-asyncio`
* `HTTPX`, the client that will perform HTTP requests. 
* `asgi-lifespan`, a library for managing the lifespan events of your FastAPI app programmatically.
* `pytest-asyncio`, an extenson for pytest that allows us to write asynchronous tests.

```python
# contextlib gives you tools for working with context managers (e.g., with)
import contextlib
from fastapi import FastAPI, status
from pydantic import BaseModel
"""
1. FastAPI starts the server.
2. It calls your lifespan context manager: prints "Startup".
3. It begins serving requests: if someone goes to /, they get {"hello": "world"}.
4. When the server is stopping: execution resumes after yield, so it prints "Shutdown".
5. App fully exits.
"""

# Treat this async function like an async context manager
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This entire lifespan function is telling FastAPI: "this entire lifespan function is telling FastAPI"
    """
    # In a real app, this is where you’d open DB connections, load models into memory, warm caches, etc.
    print("Startup")
    yield
    # In a real app, you’d clean up here: close database connections, flush logs, release resources, etc.
    print("Shutdown")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def hello_world():
    return {"hello": "world"}

class Person(BaseModel):
    first_name: str
    last_name: str
    age: int

@app.post("/persons", status_code=status.HTTP_201_CREATED)
async def create_person(person: Person):
    return person

###TESTS###

import asyncio # Library for running async code and managing event loops
import httpx # A modern, async-capable HTTP client (like `requests`, but supports async) to simulate sending HTTP request to your FastAPI app during tests
import pytest # Discovers and runs test functions
import pytest_asyncio # Lets pytest handle async test functions
from asgi_lifespan import LifespanManager  # Helper that correctly handles startup and shutdown events in Asynchronous Server Gateway Interface (ASGI) apps 
from fastapi import status


@pytest.fixture(scope="session") # Reusable piece of setup/teardown code that can be injected into tests. scope="session" means this fixture is created once for the entire test session, not per test. This is important because the event loop can only exist once per session in async tests.
def event_loop():
    # Loop used to run async tests
    loop = asyncio.new_event_loop()
    # 
    yield loop
    # After all tests are done (since scope=session), the event loop is closed cleanly to release resources
    loop.close()

@pytest_asyncio.fixture # Defines an async fixture. same idea as @pytest.fixture, but async funcs are supported. 
async def test_client():
    async with LifespanManager(app): # LifespanManager handles FastAPI’s startup and shutdown events correctly inside tests. 
        async with httpx.AsyncClient(app=app, base_url="http://app.io") as test_client: # Creates an in-memory HTTP client that can directly call your FastAPI app (no network needed). It ensures that an HTTP session is ready.
            yield test_client # Makes the client available to the test functions

@pytest.mark.asyncio # Tells pytest this test is asynchronous. pytest-asyncio will run it inside the event loop defined earlier.
async def test_hello_world(test_client: httpx.AsyncClient): # The test_client fixture we created earlier is automatically injected here.
    # Sends an async HTTP GET request to the root endpoint (/)
    response = await test_client.get("/") # response is an `HTTPX Response` object containing all the data of the HTTP response: status code, headers, body.
    # Checks that the response status code is 200 (success)
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == {"hello": "world"}

@pytest.mark.asyncio
class TestCreatePerson:
    async def test_invalid(self, test_client: httpx.AsyncClient):
        payload = {"first_name": "John", "last_name": "Doe"}
        response = await test_client.post("/persons", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_valid(self, test_client: httpx.AsyncClient):
        payload = {"first_name": "John", "last_name": "Doe", "age": 30}
        response = await test_client.post("/persons", json=payload)

        assert response.status_code == status.HTTP_201_CREATED

        json = response.json()
        assert json == payload
```
## Tests for Websocket Endpoints
