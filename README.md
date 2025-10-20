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

## RESTful API
`python -m uvicorn code:app --reload`
`http://127.0.0.1:8000/docs` -> FastAPI will automatically list all your defined endpoints and provide documention about the expected inputs and outputs. You can even try each endpoint directly in this web interface.

### Handling Request Parameters
The main goal of a **representational state transfer (REST)** API is to provide a structured way to interact with data. As such, it is crucial for the end user to send some information to tialor the response they need, such as path parameters, query parameter, body payloads, headers, and so on.

` http http://localhost:800/usersHTTP/1.1`

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

- Example 1: Function has default values which means query parameters are optional. If you wish to define a **required** parameter, simply leave out the default value. In that case, you will get a `422 error` response if you omit the parameter.<br>
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

**Headers and Cookies**<br>

**The Request Object**<br>

### Customizing the Response

****

### Structuring a Bigger Project with Multiple Routers



## Resources:
* [Building Data Science Applications with FastAPI by Francois Voron - Jul 2023](https://github.com/PacktPublishing/Building-Data-Science-Applications-with-FastAPI-Second-Edition/tree/main)


