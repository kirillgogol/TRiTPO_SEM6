# from dotenv import load_dotenv
# import os
from pydantic import BaseSettings

# load_dotenv()

# DB_USER = os.getenv('USER')
# DB_PASSWORD = os.getenv('PASSWORD')
# DB_HOST = os.getenv('HOST')
# DB_NAME = os.getenv('DB_NAME')


class Settings(BaseSettings):
    USER: str
    PASSWORD: str
    HOST: str
    DB_NAME: str
    PORT: str
    DEBUG: bool

    SECRET_KEY: str
    SECRET_REFRESH_KEY: str

    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = '.env'


settings = Settings()
