from fastapi import APIRouter, Depends, status, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.db_config import get_db
import app.users.models.user_db_models as user_db_models
import app.articles.models.article_db_models as article_db_models
from app.articles.controllers.article_crud import ArticleController
from app.users.controllers.user_crud import UserController

from app.authentication.token import verify_access, refresh_token


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/all_articles')
def get_articles(request: Request, db: Session = Depends(get_db)):
    token = request.cookies
    try:
        user = verify_access(token['access_token'])
        email = user.email
        db_user = db.query(user_db_models.User).filter(user_db_models.User.email == email).first()

        if not db_user:
            raise HTTPException(status_code=401, detail='No user')
        articles = ArticleController.show_articles(db)
        return templates.TemplateResponse('index.html', context={'request': request, 'articles': articles})
    except KeyError:
        response = RedirectResponse('/login', status_code=307)
        return response
    except Exception:
        new_token = refresh_token(token['refresh_token'])
        response = RedirectResponse('/all_articles', status_code=307)
        response.set_cookie(key='access_token', value=new_token)
        return response

@router.get('/register')
def get_reg(request: Request):
    return templates.TemplateResponse('registration.html', context={'request': request})


@router.post('/register', response_class=HTMLResponse)
async def reg(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    UserController.create_user(form, db)
    return RedirectResponse('/login', status_code=307)
    # return UserController.create_user(form, db)