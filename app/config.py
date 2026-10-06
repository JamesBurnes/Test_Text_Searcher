from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "search_db"
    postgres_host: str = "db"
    postgres_port: int = 5432

    elastic_host: str = "elasticsearch"
    elastic_port: int = 9200
    elastic_index: str = "documents"

    csv_path: str = "/app/data/posts.csv"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def elastic_url(self) -> str:
        return f"http://{self.elastic_host}:{self.elastic_port}"


settings = Settings()