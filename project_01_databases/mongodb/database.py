from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class MongoBaseModel(BaseModel):
    # In a Pydantic model, if a property starts with an underscore, it's considered to be private and this, is not used as a data field for our model.
    # _id is encoded as a binary object, called ObjectId, instead of a simple integer or string. It's usually represented in the form of a string such as 6783c7d7. This type of object is not supported out of the box by Pydantic or FastAPI.
    # `alias` is a Pydantic option that allows us to change the name of the field during serialization.
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        json_encoders = {ObjectId: str}

class PostBase(MongoBaseModel):
    title: str
    content: str
    publication_date: datetime = Field(default_factory=datetime.now)

class PostPartialUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class PostCreate(PostBase):
    pass

class Post(PostBase):
    pass