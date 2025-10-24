# Pydantic Cheat Sheet
## Defining Models & Their Field Types
### Standard Field Types
```python
class Person(BaseModel):
    first_name: str
    last_name: str
    age: int

person = Person(first_name="John", last_name="Doe", age=30)
print(person)  # first_name='John' last_name='Doe' age=30
```
```python
class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    NON_BINARY = "NON_BINARY"

class Person(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    birthdate: date
    interests: list[str]

# Invalid gender
try:
    Person(
        first_name="John",
        last_name="Doe",
        gender="INVALID_VALUE",
        birthdate="1991-01-01",
        interests=["travel", "sports"],
    )
except ValidationError as e:
    print(str(e))

# Invalid birthdate
try:
    Person(
        first_name="John",
        last_name="Doe",
        gender=Gender.MALE,
        birthdate="1991-13-42",
        interests=["travel", "sports"],
    )
except ValidationError as e:
    print(str(e))

# Valid
person = Person(
    first_name="John",
    last_name="Doe",
    gender=Gender.MALE,
    birthdate="1991-01-01",
    interests=["travel", "sports"],
)
# first_name='John' last_name='Doe' gender=<Gender.MALE: 'MALE'> birthdate=datetime.date(1991, 1, 1) interests=['travel', 'sports']
print(person)
```
```python
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

# Invalid address
try:
    Person(
        first_name="John",
        last_name="Doe",
        gender=Gender.MALE,
        birthdate="1991-01-01",
        interests=["travel", "sports"],
        address={
            "street_address": "12 Squirell Street",
            "postal_code": "424242",
            "city": "Woodtown",
            # Missing country
        },
    )
except ValidationError as e:
    print(str(e))

# Valid
person = Person(
    first_name="John",
    last_name="Doe",
    gender=Gender.MALE,
    birthdate="1991-01-01",
    interests=["travel", "sports"],
    address={
        "street_address": "12 Squirell Street",
        "postal_code": "424242",
        "city": "Woodtown",
        "country": "US",
    },
)
print(person)
```
### Optional Fields and Default Values
When defining a field with the `| None` type hint, it accepts a `None` value. 
```python
class UserProfile(BaseModel):
    nickname: str
    location: str | None = None
    subscribed_newsletter: bool = True

user = UserProfile(nickname="jdoe")
print(user)  # nickname='jdoe' location=None subscribed_newsletter=True
```
Be careful, though: don't assign default values such as this for dynamic types such as datetimes. If you do, the datetime instantiation will be evaluated only once when the model is imported. The effect of this is that all the objects you instantiate will then sahre the same value instad of having a fresh value.
```python
class Model(BaseModel):
    # Don't do this.
    # This example shows you why it doesn't work.
    d: datetime = datetime.now()

o1 = Model()
print(o1.d)

time.sleep(1)  # Wait for a second

o2 = Model()
print(o2.d)

print(o1.d < o2.d)  # False
```
`Field` function allows you to apply some validation to the request parameters to check whether a number was in a certain range or whether a string matched a regular expression.
```python
class Person(BaseModel):
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    age: int | None = Field(None, ge=0, le=120)

# Invalid first name
try:
    Person(first_name="J", last_name="Doe", age=30)
except ValidationError as e:
    print(str(e))

# Invalid age
try:
    Person(first_name="John", last_name="Doe", age=2000)
except ValidationError as e:
    print(str(e))

# Valid
person = Person(first_name="John", last_name="Doe", age=30)
print(person)  # first_name='John' last_name='Doe' age=30
```
Dynamic default values: To set dynamic values, Pydantic provides the `default_factory` argument on the `Field` function to cover this use case. This argument expects you to pass a function that will be called during model instantiation. Thus, the resulting object will be evaluated at runtime each time you create a new object.
```python
def list_factory():
    return ["a", "b", "c"]

class Model(BaseModel):
    l: list[str] = Field(default_factory=list_factory)
    d: datetime = Field(default_factory=datetime.now)
    l2: list[str] = Field(default_factory=list)

o1 = Model()
print(o1.l)  # ["a", "b", "c"]
print(o1.l2)  # []

o1.l.append("d")
print(o1.l)  # ["a", "b", "c", "d"]

o2 = Model()
print(o2.l)  # ["a", "b", "c"]
print(o1.l2)  # []

print(o1.d < o2.d)  # True
```
### Validating Email Addresses and URLs
`EmailStr` and `HttpUrl` to validate an email address and a HTTP URL.

`pip install email-validator`
```python
class User(BaseModel):
    email: EmailStr
    website: HttpUrl

# Invalid email
try:
    User(email="jdoe", website="https://www.example.com")
except ValidationError as e:
    print(str(e))

# Invalid URL
try:
    User(email="jdoe@example.com", website="jdoe")
except ValidationError as e:
    print(str(e))

# Valid
user = User(email="jdoe@example.com", website="https://www.example.com")
# email='jdoe@example.com' website=HttpUrl('https://www.example.com', scheme='https', host='www.example.com', tld='com', host_type='domain')
print(user)
```
## Model Variation with Class Inheritance
Leverage model inheritane to avoud repeating ourselves a lot. Identify the fields that are common to every variation and put them in a model, which will be used as a base for every other. Then, you only have to inherit from that model to create your variations and add the specific fields.
```python
class PostBase(BaseModel):
    title: str
    content: str

    def excerpt(self) -> str:
        return f"{self.content[:140]}..."

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: int

class Post(PostBase):
    id: int
    nb_views: int = 0
```
You can also define methods on your model. Defining the `excerpt` method on `PostBase` means it'll be available in every model variation.

## Custom Data Validation
### Field Level
```python
```
### Object Level
```python
```
### Before Parsing
```python
```
## Pydantic Objects
### Object to Dictionary
```python
```
### Instance From a Sub-Class Object
```python
```
### Updating an Instance Partially
```python
```
