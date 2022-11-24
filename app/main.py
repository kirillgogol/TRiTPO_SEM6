from fastapi import FastAPI

from app.users.views.view import router as users
from app.articles.views.view import router as articles
import uvicorn

app = FastAPI()

app.include_router(users)
app.include_router(articles)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
