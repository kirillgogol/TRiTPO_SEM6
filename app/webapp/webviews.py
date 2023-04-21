from datetime import datetime
import os
from fastapi import APIRouter, Depends, Request
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
from app.articles.models.article_api_models import CategoryEnum
from app.articles.models.article_db_models import Article
from app.exceptions import *
from app.webapp.controllers.twilio_controller import *
from app.authentication.token import is_valid_password
from starlette.background import BackgroundTasks
from app.file_worker import write_file
from app.webapp.controllers.token_controller import verify_tokens


router = APIRouter()
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get('/all_articles')
async def get_articles(request: Request, db: Session = Depends(get_db)):  
    try:
        tokens_verifying_result = verify_tokens(request.cookies, db)     
        articles = ArticleDBController.get_all_articles(db)
        response = templates.TemplateResponse('index.html', 
        context={'request': request, 'articles': articles, "categories": CategoryEnum.categories})
        response.set_cookie(key='access_token', value=tokens_verifying_result.access_token)
        return response
    except KeyError or UserNotFoundError:
        return RedirectResponse('/login', status_code=302)
    except RefreshTokenExpiredError:
        return RedirectResponse('/logout', status_code=302)


@router.post('/download_file/{id}')
async def download_file(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        tokens_verifying_result = verify_tokens(request.cookies, db) 
        file = ArticleDBController.download_file(id, db)
        response = FileResponse(filename=file["filename"], path=file["path"], media_type="application/multipart")
        response.set_cookie(key='access_token', value=tokens_verifying_result.access_token)
        return response
    except KeyError or UserNotFoundError:
        return RedirectResponse('/login', status_code=302)
    except RefreshTokenExpiredError:
        return RedirectResponse('/logout', status_code=302)


@router.get('/register')
async def reg(request: Request):
    return templates.TemplateResponse('registration.html', context={'request': request})


@router.post('/register', response_class=HTMLResponse)
async def reg(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    if is_valid_password(form['password']) is False:
        return templates.TemplateResponse(
            'registration.html', 
            {'request': request, 'message': f'Пароль должен содержать не менее 6 символов'}
        )
    phone = form['phone']
    sms_verification(phone)
    return templates.TemplateResponse("twilio.html",  
    context={'request': request, "user": form})


@router.post("/twilio")
async def twilio_check(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    data = {
        'phone': form['phone'],
        'code': form['code']
    }
    if sms_verification_check(data):
        encrypted_password = pwd_context.hash(form['password'])
        user = User(
            username = form['username'],
            email = form['email'],
            password = encrypted_password
        )
        db.add(user)
        db.commit()
        return RedirectResponse('/login', status_code=307)  
    return templates.TemplateResponse("twilio.html",  
    context={'request': request, "user": form, "message": "Неверный код"})


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
    try:
        tokens_verifying_result = verify_tokens(request.cookies, db)
        categories = CategoryEnum.categories
        response = templates.TemplateResponse("create_article.html", {"request": request, "categories": categories})
        response.set_cookie(key='access_token', value=tokens_verifying_result.access_token)
        return response
    except KeyError or UserNotFoundError:
        return RedirectResponse('/login', status_code=302)
    except RefreshTokenExpiredError:
        return RedirectResponse('/logout', status_code=302)


@router.post("/create_article", response_class=HTMLResponse)
async def create_article(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        tokens_verifying_result = verify_tokens(request.cookies, db)
        form = await request.form()
        if form['file'].filename and form['url'] or not form['file'].filename and not form['url']:
            return templates.TemplateResponse("create_article.html", 
            {"request": request, 
            "message": "Статья должна содержать либо ссылку, либо прикрепленный файл",
            "categories": CategoryEnum.categories
            })

        if form["file"].filename:
            new_article = Article(
                title = form['title'],
                brief_description = form['brief_description'],
                category = form['category'],
                language = form['language'],
                file = form['file'].filename,
                user_id = tokens_verifying_result.user.id
            )
            hash_part = datetime.now()
            file_hash = str(hash_part.microsecond * hash_part.second) + form["file"].filename
            new_article.file_hash = file_hash
            form['file'].filename = file_hash
            background_tasks.add_task(write_file, form['file'])
            db.add(new_article)
            db.commit()
        else:
            new_article = Article(
                title = form['title'],
                brief_description = form['brief_description'],
                url = form['url'],
                category = form['category'],
                language = form['language'],
                user_id = tokens_verifying_result.user.id
            )
            db.add(new_article)
            db.commit()
        response = RedirectResponse('/all_articles', status_code=302)
        response.set_cookie(key='access_token', value=tokens_verifying_result.access_token)
        return response
    except KeyError or UserNotFoundError:
        return RedirectResponse('/login', status_code=302)
    except RefreshTokenExpiredError:
        return RedirectResponse('/logout', status_code=302)


@router.get("/update_article/{id}", response_class=HTMLResponse)
async def update_article(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        tokens_verifying_result = verify_tokens(request.cookies, db)

        article = db.query(Article).filter(Article.id == id).first()
        if article.user_id != tokens_verifying_result.user.id:
            raise UnothorizedAccessError

        categories = CategoryEnum.categories
        response = templates.TemplateResponse('update_article.html', 
        {"request": request, "categories": categories, "article": article}
        )
        response.set_cookie(key='access_token', value=tokens_verifying_result.access_token)
        return response
    except KeyError or UserNotFoundError:
        return RedirectResponse('/login', status_code=302)
    except RefreshTokenExpiredError:
        return RedirectResponse('/logout', status_code=302)
    except UnothorizedAccessError:
        response = RedirectResponse('/profile', status_code=302)
        response.set_cookie(key='access_token', value=tokens_verifying_result.access_token)
        return response


@router.post('/update_article/{id}', response_class=HTMLResponse)
async def update_article(id: int, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        tokens_verifying_result = verify_tokens(request.cookies, db)
        form = await request.form()

        article = db.query(Article).filter(Article.id == id).first()
        if form['file'].filename and form['url'] or not form['file'].filename and not form['url']:
            return templates.TemplateResponse("update_article.html", 
            {"request": request, 
            "message": "Статья должна содержать либо ссылку, либо прикрепленный файл",
            "categories": CategoryEnum.categories,
            "article": article
            })

        article.title = form['title']
        article.brief_description = form['brief_description']
        article.category = form['category']
        article.language = form['language']
        article.user_id = tokens_verifying_result.user.id
        article.url = form['url']
        if article.file:
            os.remove(f'files/{article.file_hash}')
        if form['file'].filename:
            article.url = None
            article.file = form['file'].filename
            hash_part = datetime.now()
            file_hash = str(hash_part.microsecond * hash_part.second) + form["file"].filename
            article.file_hash = file_hash
            form['file'].filename = file_hash
            background_tasks.add_task(write_file, form['file'])
        else:
            article.file = None
            article.file_hash = None
        db.commit()
        response = RedirectResponse('/profile', status_code=302)
        response.set_cookie(
            key='access_token', value=tokens_verifying_result.access_token
            ) 
        return response  
    except KeyError or UserNotFoundError:
        return RedirectResponse('/login', status_code=302)
    except RefreshTokenExpiredError:
        return RedirectResponse('/logout', status_code=302)


@router.get('/profile')
async def profile(request: Request, db: Session = Depends(get_db)):
    try:
        tokens_verifying_result = verify_tokens(request.cookies, db)
        user_articles = db.query(Article).filter(Article.user_id == tokens_verifying_result.user.id).all()
        response = templates.TemplateResponse(
            "profile.html", 
            {"request": request, "user": tokens_verifying_result.user, "user_articles": user_articles}
        )
        response.set_cookie(key='access_token', value=tokens_verifying_result.access_token)
        return response
    except KeyError or UserNotFoundError:
        return RedirectResponse('/login', status_code=302)
    except RefreshTokenExpiredError:
        return RedirectResponse('/logout', status_code=302)


@router.get("/filtered_articles")
async def filtered_articles(request: Request, 
    category: str, title: str, language: str, author: str,
    db: Session = Depends(get_db)):
    try:
        tokens_verifying_result = verify_tokens(request.cookies, db)

        query = db.query(Article)

        if category != "Any":
            query = query.filter(Article.category.contains(category))
        if title != "":
            query = query.filter(Article.title.contains(title))
        if language != "Any":
            query = query.filter(Article.language == language)
        if author != "":
            query = query.filter(Article.author.has(email = author))
        articles = query.all()
        response = templates.TemplateResponse('index.html', 
        context={'request': request, 'articles': articles, "categories": CategoryEnum.categories})
        response.set_cookie(key='access_token', value=tokens_verifying_result.access_token)
        return response
    except KeyError or UserNotFoundError:
        return RedirectResponse('/login', status_code=302)
    except RefreshTokenExpiredError:
        return RedirectResponse('/logout', status_code=302)
