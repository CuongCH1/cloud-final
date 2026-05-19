from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str

    aws_rds_username: str
    aws_rds_password: str
    aws_rds_host: str
    aws_rds_port: int = 5432
    aws_rds_database: str

    aws_s3_bucket_name: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    @computed_field
    @property
    def postgres_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.aws_rds_username,
            password=self.aws_rds_password,
            host=self.aws_rds_host,
            port=self.aws_rds_port,
            path=self.aws_rds_database,
        )


SETTINGS = Settings()  # type: ignore
