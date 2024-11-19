import uvicorn
from src.applications.router import router as application_router
from fastapi import FastAPI, Depends
from fastapi_users import FastAPIUsers
from src.setting import settings
from src.auth.auth import auth_backend
from src.auth.database import User
from src.auth.manager import get_user_manager
from src.auth.schemas import UserRead, UserCreate

"""Блок, связанный с регистрацией и  аунтификацией"""

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app = FastAPI(title = 'TheNest')


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=settings.registration.prefix,
    tags=[settings.registration.tags],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=settings.auth.prefix,
    tags=[settings.auth.tags],
)
current_user = fastapi_users.current_user()

@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.email}"

"""Блок, связанный с заявками"""

app.include_router(
    application_router,
    prefix=settings.application.prefix,
    tags=[settings.application.tags]
)

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)