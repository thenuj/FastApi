from fastapi import FastAPI, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
import models
from models import Todos
from database import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    desc: str = Field(min_length=3,max_length=100)
    priority: int = Field(gt=0,lt=6)
    progress: bool

@app.get("/",status_code=status.HTTP_200_OK)
async def get_todos(db: db_dependency):
    return db.query(Todos).all()

@app.get("/todos/{todo_id}" , status_code=status.HTTP_200_OK)
async def get_todo_by_id(db:db_dependency,todo_id:int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(404, detail='Todo not found')

@app.post("/todos/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_req: TodoRequest):
    todo_model = Todos(**todo_req.model_dump())
    db.add(todo_model)
    db.commit()

@app.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def create_todo(db: db_dependency, todo_req: TodoRequest, todo_id:int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(404, detail='Todo Not Found')
    todo_model.title = todo_req.title
    todo_model.desc = todo_req.desc
    todo_model.priority = todo_req.priority
    todo_model.progress = todo_req.progress

    db.add(todo_model)
    db.commit()

@app.delete("/todo/delete_todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db:db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        db.delete(todo_model)
        db.commit()
    else:
        raise HTTPException(404,detail='Todo Not Found')