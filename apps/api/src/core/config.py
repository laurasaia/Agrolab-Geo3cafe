"""Application configuration module."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	"""Application settings loaded from .env file."""

	db_user: str
	db_pass: str
	db_url: str
	db_name: str
	api_port: int
	env: str
	jwt_secret: str
	jwt_algorithm: str
	jwt_expiration_minutes: int

	class Config:
		"""Pydantic configuration to load environment variables."""

		env_file = ".env"


settings = Settings()
