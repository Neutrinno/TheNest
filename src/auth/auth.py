from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy

from src.auth.manager import get_user_manager
from src.models import User

cookie_transport = CookieTransport(cookie_name = "dorm", cookie_max_age=3600)

SECRET = "SECRET"

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(name="jwt",
                                     transport=cookie_transport,
                                     get_strategy=get_jwt_strategy)

fastapi_users = FastAPIUsers[User, int](get_user_manager,[auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_user = fastapi_users.current_user(optional=True)
user_authenticator = fastapi_users.authenticator
get_current_user_token = user_authenticator.current_user_token(active=True, verified=False)