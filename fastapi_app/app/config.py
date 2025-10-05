from pydantic import BaseSettings


class Settings(BaseSettings):
    LOGSTASH_HOST: str = "localhost"
    LOGSTASH_PORT: int = 5000
    APP_NAME: str = "demo-api"
    ES_HOST: str = "http://localhost:9200"


class Config:
    env_file = ".env"


settings = Settings()