# Authentication & Security
## Security Dependencies in FastAPI
Lots of standards have been proposed. List of the most common ones:
* **Basic HTTP authentication**: In this scheme, user credentials (usually, an identifier such as an email address and password) are put into an HTTP header called `Authorization`. The value consists of the `Basic` keyword, followed by the user credentials encoded in `Base64`. This is very simple scheme to implement but not very secure since the password appears in every request.
* **Cookies**: Cookies are a useful way to store static data on the client side, usually on web browsers, that is sent in each request to the server. Typically, a cookie contains a session token that can be verified by the server and linked to a specific user.
* **Tokens**: In the `Authorization` header: Probably the most used header in a REST API context, this simply consists of sending a token in an HTTP `Authorization` header. The token is often prefixed by a method keyword, such as `Bearer`. On the server side, this token can be verified and linked to a specific user.

```python
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import APIKeyHeader

API_TOKEN = "SECRET_API_TOKEN"

app = FastAPI()
api_key_header = APIKeyHeader(name="Token")

@app.get("/protected-route")
async def protected_route(token: str = Depends(api_key_header)):
    if token != API_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return {"hello": "world"}
```
You can wrap the logic that checks the token value in its own dependency to reuse it across your endpoints.

This technique is very good candidate to be used as routers or global dependencies to protect whole sets of routes.

```python
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import APIKeyHeader

API_TOKEN = "SECRET_API_TOKEN"

app = FastAPI()

async def api_token(token: str = Depends(APIKeyHeader(name="Token"))):
    if token != API_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@app.get("/protected-route", dependencies=[Depends(api_token)])
async def protected_route():
    return {"hello": "world"}
```

This is a very basic example of adding authorization to your API. In this example, we don't have any user management; we are only checking that a token corresponds to a constant value. While it could be useful for private microservices that are not intended to be called by end users, this approach should not be considered very secure.

First, make sure your API is always served using HTTPs to ensure your token is not exposed in the headers. Then, if it's a private microservice, you should also consider not exposing it publicly on the internet and making sure only trusted servers can call it. Since you don't need users to make requests to this service, it's much safer than a simple token key that could be stolen. 
## Storing a User and their Password Securely in a Database
1. Register account on this service. Usually providing email address and a password.
2. Login.
3. In exchange, the service provides you with a session token that can be used on subsequent requests to authenticate yourself. This way, you don't have to provide your email address and password on each request, which would be annoying and dangerous. Usually, such session tokens have a limited lifetime, which means you'll have to log in after some time. This mitigates any security risks if the session token is stolen.

Storing a user entity in a database is no different from storing any other entity. The only thing you must be extremely cautious about is password storage. You must not store the password as plain text in your database. Why? If, unfortunately, a malicious person manages to get into your database, they'll be able to get the passwords of all your users. Since many people use the same password multiple times, the security of their accounts on other applications and websites would be seriously compromised.

To avoid a disaster like this, we can apply **cryptographic hash functions** to the password. The goal of those functions is to transform the password string into a hash value. This is designed to make it near impossible to retrieve the original data from the hash. Hence, even if your database is compromised, the passwords are still safe.

When users try to log in, we simply compute the hash of the password they input and compare it with the hash we have in our database. If they match, this means it's the right password.



## Retrieving a User and Generating an Access Token

## Securing Endpoints with Access Tokens

## Configuring CORS and Protecting Against CSRF Attacks