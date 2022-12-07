from fastapi import FastAPI
from app.users.views.view import router as users
from app.articles.views.view import router as articles
from app.authentication.authentication import router as login
from app.webapp.webviews import router as template_views
import uvicorn

app = FastAPI()

app.include_router(users)
app.include_router(articles)
app.include_router(login)
app.include_router(template_views)

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
