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

### Hashing Passwords
`pip install passlib argon2_cffi`

### Retrieving a User and Generating an Access Token
Being able to log ing. 

We'll get the credentials from the request payload, retrieve the user with the given email, and verify their password. If the user exists and their password is valid, we'll generate an access token and return it in the response.

Nature of the access token: It should be data string that uniquely identifies a user that is impossible to forge by a malicious third party. 

We'll generate a random string and store it in a dedicated table in our database, with a foreign key referring to the user. This way, when an authenticated request arrives, we simply have to check whether it exists in the database and look for the corresponding user. The advantage of this approach is that tokens are centralized and can easily be invalidated if they are compromised; we only need to delete them from the database.

To keep this example simple, we implemented a simple password comparison. Usually, it's good practice to implement a mechanism to upgrade the password hash at this stage. Imagine that a new and more robust hash algorithm has been introduced. We can take this opportunity to hash the password with this new algorithm and store it in a database. `passlib` includes a function for verifying and upgrading the hash in one operation.

## Configuring CORS and Protecting Against CSRF Attacks
Backends are now only responsible for data storage and retrieving and executing business logic.

From the JS code, the user interface can then just spawn requests to your API and handle the result to present it. However, we must still handle authentication: we want our user to be able to log in to the frontend application and make authenticated requests to the API. While an Authorization header, as we've seen so far, could work, there is a better way to handle authentication when working in browsers: **cookies**!

**Cross-Site Request Forgery (CSRF)**: An attacker on another website tries to trick a user who is currently authenticated with your application to perform a request on your server. Since browsers tend to send cookies with every request, your server wouldn't be able to tell that the request was actually forged. Since it's the users themselves who unintentionally launched the malicious request, these kinds of attacks don't aim to steal data but to execute operations that change the state of the application, such as changing an email address or making a money transfer. Simple requests such us `GET`, `POST`, or `HEAD` methods don't use custom headers or unusual content types and for them, the same-origin policy is not enough to protect us against CSRF attacks.

Browsers don't allow cross-origin resource sharing (CORS) HTTP requests, meaning domain A can't make requests to domain B. This follows that is called a **same-origin policy**. This is a good thing in general as it's the first barrier to preventing CSRF attacks.



