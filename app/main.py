from fastapi import FastAPI

import app.models as model
from app.config import engine

 
model.Base.metadata.create_all(bind=engine)

app = FastAPI()
