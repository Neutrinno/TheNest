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

class DistributionPrefix(BaseModel):
    prefix: str = "/distribution"
    tags: str = "distribution"

class RedistributionPrefix(BaseModel):
    prefix: str = "/redistribution"
    tags: str = "redistribution"

class PagesPrefix(BaseModel):
    prefix: str = "/page"
    tags: str = "page"


class Settings(BaseSettings):
    application: ApplicationPrefix = ApplicationPrefix()
    auth: AuthPrefix = AuthPrefix()
    registration: RegisterPrefix = RegisterPrefix()
    distribution: DistributionPrefix=DistributionPrefix()
    redistribution: RedistributionPrefix=RedistributionPrefix()
    pages: PagesPrefix = PagesPrefix()

settings = Settings()