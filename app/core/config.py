from pydantic import BaseSettings


class Settings(BaseSettings):

    DATABASE_URL: str = "postgresql://postgres:password@localhost/smartmenu"

    SECRET_KEY: str = "supersecretkey"

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()