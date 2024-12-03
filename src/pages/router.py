from fastapi import APIRouter, Request, Depends, HTTPException, Response, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from src.auth.auth import current_user
from src.models import User

router = APIRouter()

templates = Jinja2Templates(directory='src/templates')

async def auth_redirect(user: User = Depends(current_user)):
    if user is None:
        raise HTTPException(status_code=302, detail="Not authorized", headers={"Location": "/auth"})
    return user

def mixin_redirect(res: Response, path: str ='/'):
    redirect = RedirectResponse(path, status_code=status.HTTP_303_SEE_OTHER)
    redirect.raw_headers.extend(res.raw_headers)
    return redirect


@router.get('/base')
def get_base_html(request: Request):
    return templates.TemplateResponse(name='base.html', context={'request': request})

@router.get("/")
async def authorized(request: Request, user: User = Depends(auth_redirect)):
    return templates.TemplateResponse(name="authorized.html", request=request)

@router.get("/auth")
async def get_auth(request: Request, user: User = Depends(current_user)):
    if user is not None:
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(name="auth.html", request=request)

@router.get("/register")
async def get_register(request: Request, user: User = Depends(current_user)):
    if user is not None:
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(name="register.html",request=request)

@router.get("/create_application", response_class=HTMLResponse)
async def show_create_application_form(request: Request):
    return templates.TemplateResponse("application.html", {"request": request})

@router.get("/{student_id}", response_class=HTMLResponse)
async def get_main_page(request: Request, student_id: int, user: User = Depends(auth_redirect)):
    if user.id != student_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return templates.TemplateResponse("main.html", {"request": request, "student_id": user.id})
