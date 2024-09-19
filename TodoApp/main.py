from fastapi import FastAPI
import models
from routers import auth, todos
from database import engine

#instance of fastapi
app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# includes the endpoints written in auth.py,todos.py
app.include_router(auth.router)
app.include_router(todos.router)
