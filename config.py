from typing import List

from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SECRET_KEY: str

    CLIENT_ORIGIN: str

    JWT_SECRET_KEY: str
    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str
    JWT_ALGORITHM: str
    JWT_ENCODE_ISSUER: str
    JWT_DECODE_ISSUER: str
    JWT_ACCESS_TOKEN_EXPIRES: int
    JWT_REFRESH_TOKEN_EXPIRES: int
    JWT_DENYLIST_ENABLED: bool
    JWT_DENYLIST_TOKEN_CHECKS: str

    class Config:
        env_file = './.env'


settings = Settings()