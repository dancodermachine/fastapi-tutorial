from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Connection to the whole server. AsyncIOMotorClient simply expects a connection string to your database. Generally, it consists of the scheme, followed by authentication information, and the hostname of the database server. 
motor_client = AsyncIOMotorClient("mongodb://localhost:27017")
# Single database instance
database = motor_client["chapter06_mongo"]

def get_database() -> AsyncIOMotorDatabase:
    return database