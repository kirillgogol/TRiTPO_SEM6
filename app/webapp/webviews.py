from fastapi import APIRouter, Depends, status, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from app.db_config import get_db
import app.users.models.user_db_models as user_db_models
from app.articles.controllers.article_db_controller import ArticleDBController
from app.users.controllers.user_db_controller import UserDBController
from app.users.models.user_db_models import User
from passlib.context import CryptContext
from app.authentication import token
from app.authentication.token import verify_access, refresh_token
from app.articles.models.article_api_models import CategoryEnum
from app.articles.models.article_db_models import Article
from app.exceptions import *
import asyncio
from app.webapp.controllers.twillio_controller import *
from random import randint


router = APIRouter()
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get('/all_articles')
async def get_articles(request: Request, db: Session = Depends(get_db)):
    token = request.cookies
    try:
        user = verify_access(token['access_token'])
        email = user.email
        db_user = db.query(user_db_models.User).filter(user_db_models.User.email == email).first()

        if not db_user:
            raise HTTPException(status_code=401, detail='No user')
        articles = ArticleDBController.get_all_articles(db)
        return templates.TemplateResponse('index.html', context={'request': request, 'articles': articles})
    except KeyError:
        response = RedirectResponse('/login', status_code=307)
        return response
    except AccessTokenExpiredError:
        try:
            new_token = refresh_token(token['refresh_token'])
            response = RedirectResponse('/all_articles', status_code=307)
            response.set_cookie(key='access_token', value=new_token)
            return response
        except RefreshTokenExpiredError:
            return RedirectResponse('/logout', status_code=307)
    

@router.post('/download_file/{id}')
async def download_file(id: int, request: Request, db: Session = Depends(get_db)):
    token = request.cookies
    try:
        user = verify_access(token['access_token'])
        email = user.email
        db_user = db.query(user_db_models.User).filter(user_db_models.User.email == email).first()

        if not db_user:
            raise HTTPException(status_code=401, detail='No user')
        file = ArticleDBController.download_file(id, db)
        print(f"\n\n\n\n{file}\n\n\n\n")
        return FileResponse(filename=file["filename"], path=file["path"], media_type="application/pdf")
    except KeyError:
        response = RedirectResponse('/login', status_code=307)
        return response
    except AccessTokenExpiredError:
        try:
            new_token = refresh_token(token['refresh_token'])
            response = RedirectResponse('/all_articles', status_code=307)
            response.set_cookie(key='access_token', value=new_token)
            return response
        except RefreshTokenExpiredError:
            return RedirectResponse('/logout', status_code=307)


@router.get('/register')
async def reg(request: Request):
    return templates.TemplateResponse('registration.html', context={'request': request})


SMS_CODE = 0000


@router.post('/register', response_class=HTMLResponse)
async def reg(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    phone = form['phone']

    SMS_CODE = randint(1000, 9999)
    await asyncio.get_event_loop().run_in_executor(
        None, send_sms, phone, str(SMS_CODE))

    return templates.TemplateResponse("twillio.html",  
    context={'request': request, "user": form})
    # encrypted_password = pwd_context.hash(form['password'])
    # user = User(
    #     username = form['username'],
    #     email = form['email'],
    #     password = encrypted_password
    # )
    # db.add(user)
    # db.commit()
    # return RedirectResponse('/login', status_code=307)


# @router.get("/twillio")
# async def test_twillio(request: Request):

#     return templates.TemplateResponse("twillio.html",  context={'request': request})


@router.post("/register/confirmation")
async def confirmation(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    print('\n\n\n\n\n', form["code"], SMS_CODE, '\n\n\n\n\n')
    if form["code"] == str(SMS_CODE):
        encrypted_password = pwd_context.hash(form['password'])
        user = User(
            username = form['username'],
            email = form['email'],
            password = encrypted_password
        )
        db.add(user)
        db.commit()
        return RedirectResponse('/login', status_code=307)
    else:
        return {"error": "неверный код"}


@router.get('/logout', response_class=HTMLResponse)
def logout(request: Request):
    response = RedirectResponse('/login', status_code=307)
    response.delete_cookie(key='access_token')
    response.delete_cookie(key='refresh_token')
    return response


@router.get('/login', response_class=HTMLResponse)
def login(request: Request):

    return templates.TemplateResponse('login.html', {'request': request})


@router.post('/login', response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    user = db.query(User).filter(User.email == form['email']).first()

    if not user:
        return templates.TemplateResponse(
            'login.html', 
            {'request': request, 'message': f'Нет пользователя с логином {form["email"]}'}
        )

    if not pwd_context.verify(form['password'], user.password):
        return templates.TemplateResponse(
            'login.html', 
            {'request': request, 'message': f'Неверный пароль'}
        )

    access_token_expires = token.timedelta(minutes=token.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = token.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    refresh_token_expires = token.timedelta(minutes=token.REFRESH_TOKEN_EXPIRE_MINUTES)

    refresh_token = token.create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )

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
    except AccessTokenExpiredError:
        try:
            new_token = refresh_token(token['refresh_token'])
            response = RedirectResponse('/all_articles', status_code=307)
            response.set_cookie(key='access_token', value=new_token)
            return response
        except RefreshTokenExpiredError:
            return RedirectResponse('/logout', status_code=307)
    


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
    except AccessTokenExpiredError:
        try:
            new_token = refresh_token(token['refresh_token'])
            response = RedirectResponse('/all_articles', status_code=307)
            response.set_cookie(key='access_token', value=new_token)
            return response
        except RefreshTokenExpiredError:
            return RedirectResponse('/logout', status_code=307)


@router.get('/profile')
async def profile(request: Request, db: Session = Depends(get_db)):
    token = request.cookies
    try:
        user = verify_access(token['access_token'])
        db_user = db.query(user_db_models.User).filter(user_db_models.User.email == user.email).first()
        user_articles = db.query(Article).filter(Article.user_id == db_user.id).all()

        return templates.TemplateResponse(
            "profile.html", 
            {"request": request, "user": db_user, "user_articles": user_articles}
        )
    except KeyError:
        response = RedirectResponse('/login', status_code=302)
        return response
    except AccessTokenExpiredError:
        try:
            new_token = refresh_token(token['refresh_token'])
            response = RedirectResponse('/all_articles', status_code=307)
            response.set_cookie(key='access_token', value=new_token)
            return response
        except RefreshTokenExpiredError:
            return RedirectResponse('/logout', status_code=307)


@router.get("/filtered_articles")
async def filtered_articles(request: Request, 
    category: str, title: str, language: str, author: str,
    db: Session = Depends(get_db)):

    query = db.query(Article)

    if category != "":
        query = query.filter(Article.category.contains(category))

    if title != "":
        query = query.filter(Article.title.contains(title))

    if language != "Any":
        query = query.filter(Article.language == language)

    if author != "":
        query = query.filter(Article.author.has(email = author))

    articles = query.all()

    return templates.TemplateResponse('index.html', context={'request': request, 'articles': articles})
