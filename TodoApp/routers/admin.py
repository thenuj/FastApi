from fastapi import Depends, HTTPException, Path, APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from models import Todos
from database import SessionLocal
from .auth import get_current_user

#instance of fastapi
router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todo",status_code=status.HTTP_200_OK)
async def get_all_todos(user:user_dependency, db:db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(401,detail='Invalid User')
    return db.query(Todos).all()

@router.delete("/todo/delete_todo/{todo_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,db:db_dependency,
                      todo_id: int = Path(gt=0)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(401,detail='Invalid User')
    todo_model = db.query(Todos).filter(Todos.id == todo_id ).first()
    if todo_model is not None:
        db.delete(todo_model)
        db.commit()
    else:
        raise HTTPException(404,detail='Todo Not Found')