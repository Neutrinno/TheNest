from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory='src/templates')

@router.get('/base')
def get_students_html(request: Request):
    return templates.TemplateResponse(name='base.html', context={'request': request})
