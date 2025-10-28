# FastAPI Tutorial

Step-by-step tutorial for learning FastAPI and building modern web APIs with Python.

## 1. Development Environment Setup - Windows

### Install `pyenv`
`pyenv` helps you manage and switch between multiple Python versions on your system.

1. Install pyenv (Windows) `git clone https://github.com/pyenv-win/pyenv-win.git ~/.pyenv`
2. Tell your Bash shell where to find it.
    ```bash
    echo 'export PYENV="$HOME/.pyenv"' >> ~/.bashrc
    echo 'export PATH="$PYENV/pyenv-win/bin:$PYENV/pyenv-win/shims:$PATH"' >> ~/.bashrc
    ```

    **First Command**

    ```bash
    echo 'export PYENV="$HOME/.pyenv"' >> ~/.bashrc
    ```
    * `echo '...'` simply prints whatever text is inside the quotes.
    * `export PYENV="$HOME/.pyenv"` is the text we are printing.
        - `PYENV` is the name of the environment variable.
        - It's being set to `$HOME/.pyenv`
        - `$HOME` means your home directory e.g., `C:/Users/Daniel`
    * `>> ~/.bashrc`
        - `>>` means *append the output to a file.*
        - `~/.bashrc` is your Bash configuration file (a hidden file in your home directory). 
    * In plain English: *Add a line to my Bash configuration file that defines where pyenv is installed*

    **Second Command**
    ```bash
    echo 'export PATH="$PYENV/pyenv-win/bin:$PYENV/pyenv-win/shims:$PATH"' >> ~/.bashrc
    ```
    * `echo 'export PATH=...'` prints the command `export PATH=...` to be appended to `.bashrc`
    * `$PYENV/pyenv-win/bin` contains the core pyenv command itself.
    * `$PYENV/pyenv-win/shims` contains shim executables, which act as lightweight wrappers for different Python versions.
    * By putting them before `$PATH`, you ensure:
        - When you type `python`, the system finds the `pyenv` shim first (not the Windows Store one).
        - When you type `pyenv`, it finds the real `pyenv-win` command.
    * In plain English: *Tell my shell to look in pyenv's folders first whenever I run commands*.
    * `>> ~/.bashrc` this appends the line to your `.bashrc`, so it runs automatically in every future terminal session. 

3. `exec "$SHELL"`

4. Useful commands:
    * `pyenv install --list` to see the list of python versions you can install.
    * `pyenv versions` to see the list of python versions you have already installed.
    * `pyenv install <VERSION>` to install the python version you want.
    * `pyenv local <VERSION>` sets the Python version for a specific project or directory.
        - When you run `pyenv local 3.10.6` (for example), it creates a file named `.python-version` in your current directory.
        - Whenever you’re inside that directory (or any subdirectory), `pyenv` automatically switches to use that Python version.
        - If you move to another folder without a `.python-version` file, it stops using that version.  
    * `pyenv global <VERSION>` sets the default (system-wide) Python version for your user account.

### Create a Python Virtual Environment
By default, when you install a third-party package with `pip`, it will install it for the *whole system*. This is different from some other languages, such as `Node.js`' `npm`, which by default creates a local directory for the current project to install those dependencies.

This is why Python developers generally use **virtual environments**. Basically, a virtual environment is just a directory in your project containing a copy of your Python installation and the dependencies of your project.

1. `python -m venv venv` to create a virual environment.
2. `source venv/Scripts/activate` to activate this virual environment.
    * Remember that the activation of this virtual environment is only available for the *current session*. If you close it or open other command prompts, you'll have to activate it again.
3. `deactivate` to deactivate the environment.     

`pip install fastapi "uvicorn[standard]"` Sometimes, some libraries have sub-dependencies that are not required to make the library work. Usually, they are needed for optional features or specific project requirements. The square brackets are here to indicate that we want to install the standard sub-dependencies of `uvicorn`


### Installing the `HTTPie` Command-Line Utility
We need a tool to make HTTP requests to our API.
* **FastAPI** automatic documentation.
* **Postman**: a GUI tool to perform HTTP requests.
* **cURL**: The well-known and widely used command-line tool to perform network requets. It can be complex and verbose for testing simple REST APIs.
* **HTTPie**: A command-line tool aimed at making HTTP requests. Compared to cURL, its syntax is much more approchable and easier to remember, so you can run complex requests off the top of your head. Besides it comes with built-in JSON support and syntax highlighting. Since it's a **command-line interface CLI** tool, we keep all the benefits of the command line: for example, we can directly pipe a JSON file and send it as the body of an HTTP request.

`pip install httpie`

## 2. RESTful API
`python -m uvicorn code:app --reload`

`http://127.0.0.1:8000/docs` -> FastAPI will automatically list all your defined endpoints and provide documention about the expected inputs and outputs. You can even try each endpoint directly in this web interface.

### Handling Request Parameters
The main goal of a **representational state transfer (REST)** API is to provide a structured way to interact with data. As such, it is crucial for the end user to send some information to tialor the response they need, such as path parameters, query parameter, body payloads, headers, and so on.

`http http://localhost:800/usersHTTP/1.1`

**Path Parameters**<br>
The API path is the main thing that the end user will interact with.
- Normal
    ```python
    @app.get("/users/{type}/{id}")
    async def get_user(type: str, id: int):
        return {"type": type, "id": id}
    ```
- Limiting Allowed Values
    ```python
    from enum import Enum

    class UserType(str, Enum):
        STANDARD = "standard"
        ADMIN = "admin"

    @app.get("/users/{type}/{id}")
    async def get_user(type: UserType, id: int):
        return {"type": type, "id": id}
    ```
- Advanced Validation: For path parameters, the function is named Path:
    * `gt`: Greater than
    * `ge`: Greater than or equal to
    * `lt`: Less than
    * `le`: Less than or equal to
    ```python
        @app.get("/users/{id}")
        async def get_user(id: int = Path(..., ge=1)):
            return {"id": id}
    ```
    * The are also validation options for string values, which are based on length and regular expression.
    ```python
        @app.get("/license-plates/{license}")
        async def get_license_plate(license: str = Path(..., min_length=9, max_length=9)):
            return {"license": license}
    ```
    ```python
        @app.get("/license-plates/{license}")
        async def get_license_plate(license: str = Path(..., regex=r"^\w{2}-\d{3}-\w{2}$")):
            return {"license": license}
    ```

**Query Parameters**<br>
Query parameters are a common way to add some dynamic parameters to a URL. You can find them at the end of the URL in the following form: `?param1=foo&param2=bar`. In a REST API, they are commonly used on read endpoints to applu pagination, a filter, a sorting order, or selecting fields.

- Example 1: Function has default values which means query parameters are optional. If you wish to define a **required** parameter, simply leave out the default value. In that case, you will get a `422 error` response if you omit the parameter.

    `curl -i "http://localhost:8000/users?page=5&size=50"`
    ```python
    @app.get("/users")
    async def get_user(page: int = 1, size: int = 10):
        return {"page": page, "size": size}
    ```
- Example 2: Query function which works same a Path parameters.
    ```python
    @app.get("/users")
    async def get_user(page: int = Query(1, gt=0), size: int = Query(10, le=100)):
        return {"page": page, "size": size}
    ```

**The Request Body**<br>
The body is the part of the HTTP request that contains raw data representing documents, files, or form submissions. In a REST API, it's usually encoded in JSON and used to create structured objects in a database. Use the `Body` function; otherwise, FastAPI will look for it inside the query parameters by default.

`http -v POST http://localhost:8000/users \
  Content-Type:application/json \
  <<< '{"name": "John", "age": 30}'`
```python
@app.post("/users")
async def create_user(name: str = Body(...), age: int = Body(...)):
    return {"name": name, "age": age}
```

Defining payload validations such as this has some major drawbacks:
1. Quite verbose and makes the path operation function prototype huge.
2. You'll need to reuse the data structure on other endpoints or in other parts of your application.

Solution: Pydantic models. It is a Python library for data validation and is based on classes and type hints. In fact, the `Path`, `Query`, and `Body` functions that we've learned about so far use Pydantic under the hood!

```python
class User(BaseModel):
    name: str
    age: int

@app.post("/users")
async def create_user(user: User):
    return user
```
Sometimes, you might have several objects that you wish to send in the same payload all at once.

```echo '{"user": {"name": "John", "age": 30}, "company": {"name": "ACME"}}' | http POST http://localhost:8000/users```
```python
class User(BaseModel):
    name: str
    age: int

class Company(BaseModel):
    name: str

@app.post("/users")
async def create_user(user: User, company: Company):
    return {"user": user, "company": company}
```
You can even add singular body values with the `Body` function.

`echo '{"user": {"name": "John", "age": 30}, "priority":1}' | http POST http://localhost:8000/users`
```python
class User(BaseModel):
    name: str
    age: int

@app.post("/users")
async def create_user(user: User, priority: int = Body(..., ge=1, le=3)):
    return {"user": user, "priority": priority}
```

**Form Data and File Uploads**<br>
`pip install python-multipart`

* Form Data:<br>
    - FastAPI will always output a JSON response by default, no matter the form of the input data.
    - FastAPI doesn't allow you to define Pydantic models to validate form data. Instead, you have to manually define each field as an argument for the path operation function.

    `http --form POST http://localhost:8000/users name=John age=30 --ignore-stdin`
    ```python
    @app.post("/users")
    async def create_user(name: str = Form(...), age: int = Form(...)):
        return {"name": name, "age": age}
    ```
* File Uploads:<br>
    - Files as bytes objects. `File` function.
    
    `http --form POST http://localhost:8000/files file@./assets/cat.jpg --ignore-stdin`
    ```python
    @app.post("/files")
    async def upload_file(file: bytes = File(...)):
        return {"file_size": len(file)}
    ```
    - One drawback to this approach is that the uploaded file is entirely stored in memory. So, while it'll work for small files, it is likely that you'll run into issues for large files.
    - To fix this problem, FastAPI provides an `UploadFile` class. This class will store the data in memory up to a certain threshol and, after this, will automatically store it on disk in a temporary location.
    
    `http --form POST http://localhost:8000/files file@./assets/cat.jpg --ignore-stdin`
    ```python
    @app.post("/files")
    async def upload_file(file: UploadFile = File(...)):
        return {"file_name": file.filename, "content_type": file.content_type}
    ``` 
    - Accepting multiple files.

    ```bash
    http --form POST http://localhost:8000/files \
    files@./assets/cat.jpg \
    files@./assets/cat.jpg \
    --ignore-stdin
    ```
    ```python
    @app.post("/files")
    async def upload_multiple_files(files: list[UploadFile] = File(...)):
    return [
        {"file_name": file.filename,
         "content_type": file.content_type} for file in files
    ]
    ```

**Headers and Cookies**<br>
Headers contain all sorts of metadata that can be useful when handling requests. A common usage is to use them for authentication, for example, via the famous `cookies`.
* The name of the argument determines the *key of the header* that we want to retrieve.
* FastAPI automatically converts the header name into lowercase
    
    `http GET http://localhost:8000 Hello:World --ignore-stdin`
    ```python
    @app.get("/")
    async def get_header(hello: str = Header(...)):
        return {"hello": hello}
    ```
* Header names are usually separated by a hyphen, `-`, it also automatically converts it into snake case.
* The user agent is an HTTP header added automatically by most HTTP clients, such as `HTTPie` or `cURL` and web browsers. It's a way for web servers to identify which kind of application made the request. In some cases, web servers can use this information to adapt the response.
    
    `http -v GET http://localhost:8000 --ignore-stdin`
    ```python
    @app.get("/")
    async def get_header(user_agent: str = Header(...)):
        return {"user_agent": user_agent}
    ```
* One special header is cookies.
* We set a default value of `None` to the `Cookie` function. This way, even if the cookie is not set in the request, FastAPI will proceed and not generate a `422` status error response.
    ``
    ```python
    @app.get("/")
    async def get_cookie(hello: str | None = Cookie(None)):
        return {"hello": hello}
    ```
* Headers and cookies are useful for implementing authentication features.

**The Request Object**<br>
Raw request object with all of the data associated with it.
``
```python
@app.get("/")
async def get_request_object(request: Request):
    return {"path": request.url.path}
```

### Customizing the Response
Returning response. You can modify status code, raising validation errors, and setting cookies.

**Path Operation Parameters**<br>
* Default is `200` status when everything goes well.
* `201` status when the execution of the endpoint ends up in the creating of a new object.

    `http POST http://localhost:8000/posts title="Hello" --ignore-stdin`
    ```python
    class Post(BaseModel):
        title: str

    @app.post("/posts", status_code=status.HTTP_201_CREATED)
    async def create_post(post: Post):
        return post
    ```
* Interesting scenario for this option is when you have nothing to return, such as when you delete an object. In this case, the `204` status code is a good fit.
    ```python
    # Dummy database
    posts = {
        1: Post(title="Hello", nb_views=100),
    }

    @app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_post(id: int):
        posts.pop(id, None)
        return None
    ```
* Sometimes you will find differences between the input data, the data you store in your database, and the data you want to show to the end user.
    `http GET http://localhost:8000/posts/1 --ignore-stdin`
    ```python
    class Post(BaseModel):
        title: str
        nb_views: int

    class PublicPost(BaseModel):
        title: str

    # Dummy database
    posts = {
        1: Post(title="Hello", nb_views=100),
    }

    @app.get("/posts/{id}", response_model=PublicPost)
    async def get_post(id: int):
        return posts[id]
    ```

**The Response Parameter**<br>
Sometimes you want to return some custom headers or set cookies by injecting the `Response` object as an argument of the path operation function.
* Setting Headers: The `Response` object gives you access to a set of properties, including `headers`. It's a simple dictionary where the key is the name of the header, and the value is its associated value. Also, you don't have to return the `Response` object. You can still return JSON-encodable data.
    
    `http GET http://localhost:8000 --ignore-stdin`
    ```python
    @app.get("/")
    async def custom_header(response: Response):
        response.headers["Custom-Header"] = "Custom-Header-Value"
        return {"hello": "world"}
    ```
* Setting Cookies: Cookies are useful when you want the user's state within the browser between each of their visits.

    `http GET http://localhost:8000 --ignore-stdin`
    ```python
    @app.get("/")
    async def custom_cookie(response: Response):
        # It'll be valid for 86,400 seconds before the browser removes it.
        response.set_cookie("cookie-name", "cookie-value", max_age=86400)
        return {"hello": "world"}
    ```
* Setting the Status Code Dynamically: This won't be detected by the automatic documentation.

`http PUT http://localhost:8000/posts/1 title="Updated title" --ignore-stdin`
`http PUT http://localhost:8000/posts/2 title="New title" --ignore-stdin`
```python
class Post(BaseModel):
    title: str

# Dummy database
posts = {
    1: Post(title="Hello"),
}

@app.put("/posts/{id}")
async def update_or_create_post(id: int, post: Post, response: Response):
    if id not in posts:
        response.status_code = status.HTTP_201_CREATED
    posts[id] = post
    return posts[id]
```

**Raising HTTP errors**<br>
Wrong parameters, invalid payloads, or objects that don't exist anymore. It is critical to detect errors and raise a clear and unambiguous error message to the end user so that they can correct their mistake.

`http POST http://localhost:8000/password password="aa" password_confirm="bb" --ignore-stdin`
```python
@app.post("/password")
async def check_password(password: str = Body(...), password_confirm: str = Body(...)):
    if password != password_confirm:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Passwords don't match.",
        )
    return {"message": "Passwords match."}
```
You are not limited to a simple string for the error message: you can return a dictionary or a list in order to get structured information about the error.

`http POST http://localhost:8000/password password="aa" password_confirm="bb" --ignore-stdin`
```python
@app.post("/password")
async def check_password(password: str = Body(...), password_confirm: str = Body(...)):
    if password != password_confirm:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Passwords don't match.",
                "hints": [
                    "Check the caps lock on your keyboard",
                    "Try to make the password visible by clicking on the eye icon to check your typing",
                ],
            },
        )
    return {"message": "Passwords match."}
```

**Building a Custom Response**<br>
* `JSONResponse`: This response class takes care of serialising some data to JSON and adding the correct `Content-Type` header. 
* `HTMLResponse`: This can be used to return an HTML response.
* `PlainTextResponse`: This can be used to return raw text.
    ```python
    @app.get("/html", response_class=HTMLResponse)
    async def get_html():
        return """
            <html>
                <head>
                    <title>Hello world!</title>
                </head>
                <body>
                    <h1>Hello world!</h1>
                </body>
            </html>
        """

    @app.get("/text", response_class=PlainTextResponse)
    async def text():
        return "Hello world!"
    ```
* `RedirectResponse`: This can be used to make a redirection. A HTTP response with a **Location** header pointing to the new URL and a status code in the 3xxrange.
    ```python
    @app.get("/redirect")
    async def redirect():
        return RedirectResponse("/new-url")
    ```
    ```python
    # By default, it'' use the 307 Temporary Redirect status code, but you can change this through the `status_code` argument. 
    @app.get("/redirect")
    async def redirect():
        return RedirectResponse("/new-url", status_code=status.HTTP_301_MOVED_PERMANENTLY)
    ```
* `StreamingResponse`: This can be used to stream a flow of bytes.
* `FileResponse`: This can be used to automatically build a proper file response given the path of a file on the local disk. Usefful when you want to propose some files to download. This class will automatically take care of opening the file on disk and streaming the bytes along with the proper HTTP headers.
    ```python
    @app.get("/cat")
    async def get_cat():
        root_directory = Path(__file__).parent.parent
        picture_path = root_directory / "assets" / "cat.jpg"
        return FileResponse(picture_path)
    ```
* Custom response
    ```python
    @app.get("/xml")
    async def get_xml():
        content = """<?xml version="1.0" encoding="UTF-8"?>
            <Hello>World</Hello>
        """
        return Response(content=content, media_type="application/xml")
    ```
### Structuring a Bigger Project with Multiple Routers
```
project_example/
|── schemas/
|    |── __init__.py
|    |── post.py
|    |── user.py
|── routers/
|     |── __init__.py
|     |── posts.py
|     |── users.py
|── __init__.py
|── app.py
|── db.py
```
**Routers** are "sub-parts" of your API and are usually dedicated to a single type of object, such as `users` or `posts`, which are defined on their own files. The `schemas` folder contains the Pydantic models.

The good thing about routrs is that you can even nest them and include sub-routers in routers that include other routers themselves. Therefore, you can have a quite complex routing hierarchy with very low effort.

## Resources:
* [Building Data Science Applications with FastAPI by Francois Voron - Jul 2023](https://github.com/PacktPublishing/Building-Data-Science-Applications-with-FastAPI-Second-Edition/tree/main)


