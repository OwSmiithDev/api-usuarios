from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str
    TEST_DATABASE_URL: str = ""
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    RAIO_VIZINHANCA: int = 2
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
