from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    TG_TOKEN: str = Field(env='TG_TOKEN')

    class Config:
        env_file = './.env'


config = Settings()