from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Users
from routers.auth import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['Users']
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[str,Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

class Password(BaseModel):
    new_pass:str

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user:user_dependency, db:db_dependency):
    if user is None:
        raise HTTPException(401,detail='Invalid User')
    return db.query(Users).filter(Users.id == user.get('user_id')).first()

@router.put("/change_pass",status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user:user_dependency, db: db_dependency, password:Password):
    if user is None:
        raise HTTPException(401,detail='Invalid User')
    user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()
    if bcrypt_context.verify(password.new_pass, user_model.hashed_password):
        raise HTTPException(401,detail='Please enter new password')
    user_model.hashed_password = bcrypt_context.hash(password.new_pass)
    db.add(user_model)
    db.commit()