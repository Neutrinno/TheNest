from typing import Union

import uvicorn
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.authentication import Strategy, Authenticator
from fastapi.responses import RedirectResponse
from fastapi_users.schemas import BaseUserCreate

from src.applications.router import router as application_router
from src.distribution.router import router as distribution_router
from src.redistribution.router import router as redistribution_router
from fastapi import FastAPI, Depends, Form, Request, Response, status, HTTPException
from fastapi_users import FastAPIUsers, BaseUserManager, exceptions
from src.setting import settings
from src.auth.auth import auth_backend, current_active_user, get_current_user_token, current_user
from src.auth.database import User
from src.auth.manager import get_user_manager
from src.auth.schemas import UserRead, UserCreate
from src.pages.router import router as pages_router, templates
from fastapi.staticfiles import StaticFiles


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

@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.email}"

"""Блок, связанный с заявками"""

app.include_router(
    application_router,
    prefix=settings.application.prefix,
    tags=[settings.application.tags]
)

app.include_router(
    distribution_router,
    prefix=settings.distribution.prefix,
    tags=[settings.distribution.tags]
)

app.include_router(
    redistribution_router,
    prefix=settings.redistribution.prefix,
    tags=[settings.redistribution.tags]
)

app.include_router(
    pages_router,
    prefix=settings.pages.prefix,
    tags=[settings.pages.tags]
)

#app.mount("/src/static", StaticFiles(directory="src/static"), name="static")


async def auth_redirect(user: User = Depends(current_user)):
    if user is None:
        raise HTTPException(status_code=302, detail="Not authorized", headers={"Location": "/auth"})
    return user


@app.get("/")
async def authorized(request: Request, user: User = Depends(auth_redirect)):
    return templates.TemplateResponse(name="authorized.html", request=request)


@app.get("/auth")
async def get_auth(request: Request, user: User = Depends(current_user)):
    if user is not None:
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(name="auth.html", request=request)



if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)