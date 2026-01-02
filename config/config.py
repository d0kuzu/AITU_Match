from dataclasses import dataclass
from pathlib import Path

from environs import Env


env = Env()
if Path(".env").exists():
    env.read_env(".env")


@dataclass(frozen=True)
class DatabaseConfig:
    host: str = env.str("DB_HOST")
    port: int = env.int("DB_PORT")
    user: str = env.str("DB_USER")
    password: str = env.str("DB_PASSWORD")
    dbname: str = env.str("DB_NAME")

    @property
    def psycopg_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.dbname}"
        )

    @property
    def asyncpg_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.dbname}"
        )


@dataclass(frozen=True)
class BotConfig:
    token: str = env.str("BOT_TOKEN")
    logging_level: int = env.int("LOGGING_LEVEL")
    admin_ids: set[int] = (7278477437,)


@dataclass(frozen=True)
class RedisConfig:
    host: str = env.str("REDIS_HOST")
    port: int = env.int("REDIS_PORT")
    db: int = env.int("REDIS_DB")


@dataclass(frozen=True)
class Environ:
    db: DatabaseConfig = DatabaseConfig()
    bot: BotConfig = BotConfig()
    redis: RedisConfig = RedisConfig()
