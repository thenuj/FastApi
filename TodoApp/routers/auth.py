from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt, JWTError
from TodoApp.database import SessionLocal
from TodoApp.models import Users
from passlib.context import CryptContext


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '074f42a6286d0e56eaa8a601dab6a785d53ab557f7099046c6747fd14be2694f'
ALGORITHM = 'HS256'


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
form_data = Annotated[OAuth2PasswordRequestForm,Depends()]
Oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
# examples of dependency injection

templates = Jinja2Templates(directory="TodoApp/templates")

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
# Hashing algorithm of bcrypt


class CreateUserRequest(BaseModel):
    username : str
    fname : str
    lname : str
    password: str
    role:str

class Token(BaseModel):
    access_token: str
    token_type: str

### Pages ###
@router.get("/login-page")
def render_login_page(request:Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page")
def render_register_page(request:Request):
    return templates.TemplateResponse("register.html", {"request": request})


### Endpoints ###
def authenticate_user(username, password, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(401, detail='Invalid User')
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(401, detail='Invalid User')
    return user
# authenticates user from db

def create_access_token(username:str, user_id:int,role:str, expires_delta:timedelta):
    encode = {'username':username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)
# encodes the JWT token
# this will encode and send the username and user_id and expire delta will
# make sure that the token expires after certain time which we pass in the function as expire_delta

async def get_current_user(token:Annotated[str,Depends(Oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        username: str = payload.get('username')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(401, detail='Invalid User')
        return {'username': username, 'user_id':user_id,'role':user_role}
    except JWTError:
        raise HTTPException(401, detail='Invalid User')
# decodes the jwt token


@router.post("/create_user",status_code=status.HTTP_201_CREATED)
async def create_user(db : db_dependency,create_user_request:CreateUserRequest):
    create_user_model = Users(
        username = create_user_request.username,
        fname = create_user_request.fname,
        lname = create_user_request.lname,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        role = create_user_request.role,
        is_active = True
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token")
async def login_for_access_token(form:form_data,db:db_dependency):
    user = authenticate_user(form.username,form.password,db)
    if not user:
        return 'Failed Authentication'
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token':token,'token_type':'bearer'}
# user1 : 1234 Anuj : 1234