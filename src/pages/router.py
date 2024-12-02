from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

router = APIRouter()

templates = Jinja2Templates(directory='src/templates')

@router.get('/base')
def get_base_html(request: Request):
    return templates.TemplateResponse(name='base.html', context={'request': request})

@router.get('/search')
def get_search_html(request: Request):
    return templates.TemplateResponse(name='search.html', context={'request': request})

@router.get("/create_application", response_class=HTMLResponse)
async def show_create_application_form(request: Request):
    return templates.TemplateResponse("application.html", {"request": request})
