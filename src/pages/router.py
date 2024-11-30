from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from src. auth. manager import get_user_manager
router = APIRouter()

templates = Jinja2Templates(directory='src/templates')

@router.get('/base')
def get_base_html(request: Request):
    return templates.TemplateResponse(name='base.html', context={'request': request})

@router.get('/search')
def get_search_html(request: Request):
    return templates.TemplateResponse(name='search.html', context={'request': request})

"""@router.get('/register', register = Depends(get_user_manager))
def get_register_html(request: Request):
    return templates.TemplateResponse(name='register.html', context={'request': request})"""