from fastapi import APIRouter, Depends, status, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.db_config import get_db
import app.users.models.user_db_models as user_db_models
from app.articles.controllers.article_crud import ArticleController
from app.users.controllers.user_crud import UserController
from app.users.models.user_db_models import User
from passlib.context import CryptContext
from app.authentication import token
from app.authentication.token import verify_access, refresh_token
from app.articles.models.article_api_models import CategoryEnum
from app.articles.models.article_db_models import Article


router = APIRouter()
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    encrypted_password = pwd_context.hash(form['password'])
    user = User(
        username = form['username'],
        email = form['email'],
        password = encrypted_password
    )
    db.add(user)
    db.commit()
    return RedirectResponse('/login', status_code=307)
    # return UserController.create_user(form, db)


@router.get('/logout', response_class=HTMLResponse)
def logout(request: Request):
    response = RedirectResponse('/login', status_code=307)
    response.delete_cookie(key='access_token')
    response.delete_cookie(key='refresh_token')
    return response


@router.get('/login', response_class=HTMLResponse)
def get_login_from(request: Request):

    return templates.TemplateResponse('login.html', {'request': request})


@router.post('/login', response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    user = db.query(User).filter(User.email == form['email']).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'No user with email {form["email"]}')

    if not pwd_context.verify(form['password'], user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'Incorrect password')

    access_token_expires = token.timedelta(minutes=token.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = token.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    refresh_token_expires = token.timedelta(minutes=token.REFRESH_TOKEN_EXPIRE_MINUTES)

    refresh_token = token.create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )

    # response = templates.TemplateResponse('login.html', {'request': request, 'message': 'successfully logged in'})
    response = RedirectResponse('/all_articles', status_code=302)
    response.set_cookie(key='access_token', value=access_token)
    response.set_cookie(key='refresh_token', value=refresh_token)
    return response


@router.get("/create_article", response_class=HTMLResponse)
async def create_article(request: Request, db: Session = Depends(get_db)):
    token = request.cookies
    try:
        user = verify_access(token['access_token'])
        email = user.email
        db_user = db.query(user_db_models.User).filter(user_db_models.User.email == email).first()

        if not db_user:
            raise HTTPException(status_code=401, detail='No user')
        categories = CategoryEnum.categories
        return templates.TemplateResponse("create_article.html", {"request": request, "categories": categories})
    except KeyError:
        response = RedirectResponse('/login', status_code=302)
        return response
    except Exception:
        new_token = refresh_token(token['refresh_token'])
        response = RedirectResponse('/create_article', status_code=302)
        response.set_cookie(key='access_token', value=new_token)
        return response
    


@router.post("/create_article", response_class=HTMLResponse)
async def create_article(request: Request, db: Session = Depends(get_db)):
    token = request.cookies
    try:
        user = verify_access(token['access_token'])
        email = user.email
        db_user = db.query(user_db_models.User).filter(user_db_models.User.email == email).first()

        if not db_user:
            raise HTTPException(status_code=401, detail='No user')
        form = await request.form()
        new_article = Article(
            title = form['title'],
            brief_description = form['brief_description'],
            url = form['url'],
            category = form['category'],
            language = form['language'],
            user_id = db_user.id
        )
        db.add(new_article)
        db.commit()
        return RedirectResponse('/all_articles', status_code=302)
    except KeyError:
        response = RedirectResponse('/login', status_code=302)
        return response
    except Exception:
        new_token = refresh_token(token['refresh_token'])
        response = RedirectResponse('/all_articles', status_code=302)
        response.set_cookie(key='access_token', value=new_token)
        return response