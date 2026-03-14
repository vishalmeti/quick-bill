from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Auth Microservice"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_PLEASE_CHANGE_IN_PRODUCTION"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    AWS_ACCESS_KEY_ID: str = "dummy_access_key"
    AWS_SECRET_ACCESS_KEY: str = "dummy_secret_key"
    AWS_REGION: str = "us-east-1"
    DYNAMODB_TABLE: str = "users"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
