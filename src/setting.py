from pydantic import BaseModel
from pydantic_settings import BaseSettings

class RegisterPrefix(BaseModel):
    prefix: str = "/auth/jwt"
    tags: str = "auth"

class AuthPrefix(BaseModel):
    prefix: str = "/auth"
    tags: str = "auth"

class ApplicationPrefix(BaseModel):
    prefix: str = "/application"
    tags: str = "application"

class Settings(BaseSettings):
    application: ApplicationPrefix = ApplicationPrefix()
    auth: AuthPrefix = AuthPrefix()
    registration: RegisterPrefix = RegisterPrefix()


settings = Settings()