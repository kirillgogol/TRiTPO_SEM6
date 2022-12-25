from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from app.users.views.user_views import router as users
from app.articles.views.article_views import router as articles
from app.authentication.authentication import router as login
from app.webapp.webviews import router as template_views
from app.settings import settings
import uvicorn

app = FastAPI()

app.include_router(users)
app.include_router(articles)
app.include_router(login)
app.include_router(template_views)

app.mount(
    f'/{settings.FILE_CONTAINER_NAME}', 
    StaticFiles(directory=f"{settings.FILE_CONTAINER_NAME}"), 
    name=f"{settings.FILE_CONTAINER_NAME}"
)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
