from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", env_file=".env")
    host: str = Field(..., description="Redis host")
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False

    @property
    def url(self) -> str:
        scheme = "rediss" if self.ssl else "redis"
        auth = f":{self.password}@" if self.password else ""
        return f"{scheme}://{auth}{self.host}:{self.port}/{self.db}"

class TelegramSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TG_", env_file=".env")
    token: str