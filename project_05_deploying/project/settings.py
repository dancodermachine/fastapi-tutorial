from pydantic import BaseSettings

# To structure a settings model, all you need to do is create a class that inherits from pydantic.BaseSettings
class Settings(BaseSettings):
    debug: bool = False
    environment: str
    database_url: str

    class Config:
        # Here we tell Pydantic to look for environment variables set in a file named .env, if it's available
        env_file = ".env"

settings = Settings()