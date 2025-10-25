# Dependency Injection
## What is Dependency Injection?
Reusing logic across your project. An authentication system, a query parameter validator, or a rare limiter are typical use cases for dependencies.

Dependency injection is a system to automatically instantiate objects and the ones they depend on. The responsability of developers is then to only provide a declaration of how an object should be created, and let the system resolve all the dependency chains and create the actual objects at runtime.

FastAPI allows you to declare only the objects and variables you wish to have at hand by declaring them in the path operation function arguments.

```python
app = FastAPI()

@app.get("/")
async def header(user_agent: str = Header(...)):
    return {"user_agent": user_agent}
```

Internally, the `Header` function has some logic to automatically get the `request` object, check for the required header, return its value, or raise an error if it's not preset. From the developer's perspective, however, we don't know how it handled the required objects for this operation: we just ask for the value we need. That's dependency injection.
## Function Dependency
Dependency can be defined either as a function or as a callable class. A dependency is a way to wrap some logic that will retrieve some sub-values or sub-objects, make something with them, and finally, return a value that will be injected into the endpoint calling it.

`Depends` function's role is to take a function in the argument and execute it when the endpoint is called. The sub-dependencies are automatically discovered and executed.

`http "http://localhost:8000/items?limit=5&skip=10" --ignore-stdin `
```python
async def pagination(skip: int = 0, limit: int = 10) -> tuple[int, int]:
    return (skip, limit)

@app.get("/items")
async def list_items(p: tuple[int, int] = Depends(pagination)):
    skip, limit = p
    return {"skip": skip, "limit": limit}

@app.get("/things")
async def list_things(p: tuple[int, int] = Depends(pagination)):
    skip, limit = p
    return {"skip": skip, "limit": limit}
```
```python
async def pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
) -> tuple[int, int]:
    capped_limit = min(100, limit)
    return (skip, capped_limit)

@app.get("/items")
async def list_items(p: tuple[int, int] = Depends(pagination)):
    skip, limit = p
    return {"skip": skip, "limit": limit}

@app.get("/things")
async def list_things(p: tuple[int, int] = Depends(pagination)):
    skip, limit = p
    return {"skip": skip, "limit": limit}
```
### Getting and Object or Raising a 404 Error
In a REST API, you'll typically have endpoints to get, update, and delete a single object given its identifier in the path. On each one, you'll likely have the same logic: try to retrieve this object in the database or raise a 404 error if it doesn't exist. That's a perfect use case for a dependency.
```python
class Post(BaseModel):
    id: int
    title: str
    content: str

class PostUpdate(BaseModel):
    title: str | None
    content: str | None

class DummyDatabase:
    posts: dict[int, Post] = {}

db = DummyDatabase()
db.posts = {
    1: Post(id=1, title="Post 1", content="Content 1"),
    2: Post(id=2, title="Post 2", content="Content 2"),
    3: Post(id=3, title="Post 3", content="Content 3"),
}

async def get_post_or_404(id: int) -> Post:
    try:
        return db.posts[id]
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.get("/posts/{id}")
async def get(post: Post = Depends(get_post_or_404)):
    return post

@app.patch("/posts/{id}")
async def update(post_update: PostUpdate, post: Post = Depends(get_post_or_404)):
    updated_post = post.copy(update=post_update.dict())
    db.posts[post.id] = updated_post
    return updated_post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(post: Post = Depends(get_post_or_404)):
    db.posts.pop(post.id)
```
Another typical example of this is authentication: if the endpoint requires a user to be authenticated, we can raise a `401` error in the dependency by checking for the token or the cookie.

The only point of attention is to not forget the ID parameter in the path of those endpoints.
## Parameterized Dependency with a Class
To set some parameters on a dependency to finely tune its behaviour. We can set class properties - with the `__init__` method, for example - and use them in the logic of the dependency itself.
```python
class Pagination:
    def __init__(self, maximum_limit: int = 100):
        self.maximum_limit = maximum_limit

    async def __call__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=0),
    ) -> tuple[int, int]:
        capped_limit = min(self.maximum_limit, limit)
        return (skip, capped_limit)

pagination = Pagination(maximum_limit=50)

@app.get("/items")
async def list_items(p: tuple[int, int] = Depends(pagination)):
    skip, limit = p
    return {"skip": skip, "limit": limit}

@app.get("/things")
async def list_things(p: tuple[int, int] = Depends(pagination)):
    skip, limit = p
    return {"skip": skip, "limit": limit}
```
The other advantage of a class dependency is that it can maintain local values in memory. This property can be very useful if we have to make some heave initialization logic, such as loading a ML model, for example, which we want to do only once at startup. Then, the callable part just has to call the loaded model to make the prediction, which should be quite fast.
### Class Methods as Dependencies
Even if the `__call__` method is the most straightforward way to make a class dependency, you can directly pass a method to `Depends`.
This approach can be very useful if you have common parameters or logic that you need to reuse in slightly different cases. For example, you could have one pre-trained ML model made with `scikit-learn`. Before applying the decision function, you may want to apply different preprocessing steps, depending on the input data.
```python
class Pagination:
    def __init__(self, maximum_limit: int = 100):
        self.maximum_limit = maximum_limit

    async def skip_limit(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=0),
    ) -> tuple[int, int]:
        capped_limit = min(self.maximum_limit, limit)
        return (skip, capped_limit)

    async def page_size(
        self,
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=0),
    ) -> tuple[int, int]:
        capped_size = min(self.maximum_limit, size)
        return (page, capped_size)

pagination = Pagination(maximum_limit=50)

@app.get("/items")
async def list_items(p: tuple[int, int] = Depends(pagination.skip_limit)):
    skip, limit = p
    return {"skip": skip, "limit": limit}

@app.get("/things")
async def list_things(p: tuple[int, int] = Depends(pagination.page_size)):
    page, size = p
    return {"page": page, "size": size}
```
## Dependencies at the Path, Router, and Global Level
The main motivation for this is to be able to apply some global request validation or perform side logic on several routes without the need to add a dependency on each endpoint. Typically, an authentication method or a rate limiter could be very good candidates for this use case.
### Path Decorator
You can add a dependency on a path operation decorator instead of the arguments.
The path operation decorator accepts an argument, `dependencies`, you can add as many dependencies as you need.
```python
def secret_header(secret_header: str | None = Header(None)) -> None:
    if not secret_header or secret_header != "SECRET_VALUE":
        raise HTTPException(status.HTTP_403_FORBIDDEN)

@app.get("/protected-route", dependencies=[Depends(secret_header)])
async def protected_route():
    return {"hello": "world"}
```
### Whole Router
Inject a dependency into the whole router. 2 ways to do it.
1. Set the `dependencies` argument on the `APIRouter` class.
    ```python
    def secret_header(secret_header: str | None = Header(None)) -> None:
        if not secret_header or secret_header != "SECRET_VALUE":
            raise HTTPException(status.HTTP_403_FORBIDDEN)

    router = APIRouter(dependencies=[Depends(secret_header)])

    @router.get("/route1")
    async def router_route1():
        return {"route": "route1"}

    @router.get("/route2")
    async def router_route2():
        return {"route": "route2"}

    app = FastAPI()
    app.include_router(router, prefix="/router")
    ```
2. Set the `dependencies` argument on the `include_router` method.
    ```python
    def secret_header(secret_header: str | None = Header(None)) -> None:
        if not secret_header or secret_header != "SECRET_VALUE":
            raise HTTPException(status.HTTP_403_FORBIDDEN)

    router = APIRouter()

    @router.get("/route1")
    async def router_route1():
        return {"route": "route1"}

    @router.get("/route2")
    async def router_route2():
        return {"route": "route2"}

    app = FastAPI()
    app.include_router(router, prefix="/router", dependencies=[Depends(secret_header)])
    ```
In both cases, the `dependencies` argument expects a list of dependencies.
### Whole Application
If you have a dependency that implements some logging or rate-limiting functionality, for example, it could be interesting to execute it for every endpoint of your API.
```python
def secret_header(secret_header: str | None = Header(None)) -> None:
    if not secret_header or secret_header != "SECRET_VALUE":
        raise HTTPException(status.HTTP_403_FORBIDDEN)

app = FastAPI(dependencies=[Depends(secret_header)])

@app.get("/route1")
async def route1():
    return {"route": "route1"}

@app.get("/route2")
async def route2():
    return {"route": "route2"}
```
### Decision Tree
                                                                                            