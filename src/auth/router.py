from fastapi import Depends, Form
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, exceptions
from fastapi_users.authentication import Strategy, Authenticator
from fastapi_users.schemas import BaseUserCreate
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from src.auth.auth import auth_backend, get_current_user_token
from src.auth.manager import get_user_manager
from src.pages.router import templates


router = APIRouter()


@router.post("/auth")
async def auth_post(request: Request,
                    response: Response,
                    user_manager: BaseUserManager = Depends(get_user_manager),
                    strategy: Strategy = Depends(auth_backend.get_strategy),
                    email: str = Form(...),
                    password: str = Form(...)):

    credentials = OAuth2PasswordRequestForm(username=email, password=password)
    user = await user_manager.authenticate(credentials)
    if user is None:
        extra = {"exceptions": "there is no user with this username and password"}
        return templates.TemplateResponse(name="auth.html", request=request, context=extra)
    else:
        login_response = await auth_backend.login(strategy, user)
        await user_manager.on_after_login(user, request, login_response)

        redirect_url = "/page/admin/" if user.is_superuser else f"/{user.id}"

        redirect_response = RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
        redirect_response.headers.update(login_response.headers)

        return redirect_response


@router.post("/register")
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

    except exceptions.UserAlreadyExists:
        extra = {"exceptions": "UserAlreadyExists"}
        return templates.TemplateResponse(name="register.html", request=request, context=extra)

    return templates.TemplateResponse(name="auth.html", request=request,)


@router.post("/logout")
async def logout_post(
    user_token: Authenticator = Depends(get_current_user_token),
    strategy: Strategy = Depends(auth_backend.get_strategy)):
    user, token = user_token
    logout_response = await auth_backend.logout(strategy, user, token)

    redirect_response = RedirectResponse(url='/auth', status_code=303)
    redirect_response.headers.update(logout_response.headers)

    return redirect_response
