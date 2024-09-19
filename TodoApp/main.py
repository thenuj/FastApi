from fastapi import FastAPI, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
import models
from routers import auth, todos
from models import Todos
from database import engine, SessionLocal

#instance of fastapi
app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# includes the endpoints written in auth.py
app.include_router(auth.router)
app.include_router(todos.router)
