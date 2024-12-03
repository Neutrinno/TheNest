from typing import Union
import uvicorn
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.authentication import Strategy, Authenticator
from fastapi.responses import RedirectResponse
from fastapi_users.schemas import BaseUserCreate
from src.pages.router import router as router_pages, mixin_redirect
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


@app.post("/auth")
async def auth_post(
    request: Request,
    response: Response,
    user_manager: BaseUserManager = Depends(get_user_manager),
    strategy: Strategy = Depends(auth_backend.get_strategy),
    email: str = Form(...),
    password: str = Form(...),
):
    credentials = OAuth2PasswordRequestForm(username=email, password=password)
    user = await user_manager.authenticate(credentials)  # Аутентификация пользователя
    if user is None:
        # Если пользователь не найден, отобразить страницу с ошибкой
        extra = {"exceptions": "there is no user with this username and password"}
        return templates.TemplateResponse(name="auth.html", request=request, context=extra)
    else:
        # Авторизация успешна, выполнить логин
        response = await auth_backend.login(strategy, user)
        await user_manager.on_after_login(user, request, response)

        # Добавляем редирект на страницу пользователя
        return mixin_redirect(res=response, path=f"/{user.id}")

@app.post("/register")
async def register_post(
    request: Request,
    response: Response,
    user_manager: BaseUserManager = Depends(get_user_manager),
    email: str = Form(...),
    password: str = Form(...)):
    user = None
    try:
        user = await user_manager.create(
            user_create=BaseUserCreate(email=email, password=password)
        )
        print(user)
    except exceptions.UserAlreadyExists:
        extra = {"exceptions": "UserAlreadyExists"}
        return templates.TemplateResponse(
            name="register.html", request=request, context=extra
        )
    return templates.TemplateResponse(
        name="auth.html",
        request=request,)

@app.post("/logout")
async def logout_post(user_token: Authenticator = Depends(get_current_user_token),
                      strategy: Strategy = Depends(auth_backend.get_strategy)):
    user, token = user_token
    response = await auth_backend.logout(strategy, user, token)
    return mixin_redirect(res=response, path= 'auth')


app.include_router(router_pages)

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)