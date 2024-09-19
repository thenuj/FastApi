from fastapi import Depends, HTTPException, Path, APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from models import Todos
from database import SessionLocal
from .auth import get_current_user

#instance of fastapi
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    desc: str = Field(min_length=3,max_length=100)
    priority: int = Field(gt=0,lt=6)
    progress: bool

@router.get("/todos",status_code=status.HTTP_200_OK)
async def get_todos_for_user(user: user_dependency,db: db_dependency):
    if user is None:
        raise HTTPException(401,detail='Invalid User')
    return db.query(Todos).filter(Todos.owner_id == user.get('user_id')).all()

@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(user: user_dependency,db:db_dependency,todo_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(401, detail='Invalid User')
    todo_model = db.query(Todos).filter(Todos.id == todo_id and
                                        Todos.owner_id == user.get('user_id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(404, detail='Todo not found')

@router.post("/todos/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency, db: db_dependency, todo_req: TodoRequest):
    if user is None:
        raise HTTPException(401,detail='Invalid User')
    todo_model = Todos(**todo_req.model_dump(),owner_id = user.get('user_id'))
    db.add(todo_model)
    db.commit()

@router.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,
                      db: db_dependency, todo_req: TodoRequest,
                      todo_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(401,detail='Invalid User')
    todo_model = db.query(Todos).filter(Todos.id == todo_id and
                                        Todos.owner_id == user.get('user_id')).first()
    if todo_model is None:
        raise HTTPException(404, detail='Todo Not Found')
    todo_model.title = todo_req.title
    todo_model.desc = todo_req.desc
    todo_model.priority = todo_req.priority
    todo_model.progress = todo_req.progress

    db.add(todo_model)
    db.commit()

@router.delete("/todo/delete_todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,db:db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(401,detail='Invalid User')
    todo_model = db.query(Todos).filter(Todos.id == todo_id and Todos.owner_id == user.get('user_id')).first()
    if todo_model is not None:
        db.delete(todo_model)
        db.commit()
    else:
        raise HTTPException(404,detail='Todo Not Found')