import traceback

from fastapi import Depends, HTTPException, Path, APIRouter, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from TodoApp.models import Todos
from TodoApp.database import SessionLocal
from TodoApp.routers.auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

#instance of fastapi
router = APIRouter(
    prefix="/todos",
    tags=['Todo']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

templates = Jinja2Templates(directory="TodoApp/templates")

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3,max_length=100)
    priority: int = Field(gt=0,lt=6)
    progress: bool =Field(default=False)

###Pages###
def redirect_to_login():
       redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
       redirect_response.delete_cookie(key="access_token")
       return redirect_response


@router.get("/todo-page")
async def render_todo_page(request:Request, db:db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todos = db.query(Todos).filter(Todos.owner_id == user.get('user_id')).all()
        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})
    except Exception:
        print(traceback.format_exc())
        return redirect_to_login()

@router.get("/add-todo-page")
async def add_new_todo_page(request:Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse("add-todo.html",{"request":request, "user":user})
    except:
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def rdit_todo_page(request:Request, todo_id:int, db:db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todos = db.query(Todos).filter(Todos.id == todo_id).first()
        return templates.TemplateResponse("edit-todo.html", {"request":request,"todo":todos, "user":user})
    except:
        redirect_to_login()
###Endpoints###
@router.get("/",status_code=status.HTTP_200_OK)
async def get_todos_for_user(user: user_dependency,db: db_dependency):
    if user is None:
        raise HTTPException(401,detail='Invalid User')
    return db.query(Todos).filter(Todos.owner_id == user.get('user_id')).all()

@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(user: user_dependency,db:db_dependency,todo_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(401, detail='Invalid User')
    todo_model = db.query(Todos).filter(Todos.id == todo_id and
                                        Todos.owner_id == user.get('user_id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(404, detail='Todo not found')

@router.post("/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency, db: db_dependency, todo_req: TodoRequest):
    if user is None:
        raise HTTPException(401,detail='Invalid User')
    todo_model = Todos(**todo_req.model_dump(),owner_id = user.get('user_id'))
    db.add(todo_model)
    db.commit()

@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
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
    todo_model.description = todo_req.description
    todo_model.priority = todo_req.priority
    todo_model.progress = todo_req.progress

    db.add(todo_model)
    db.commit()

@router.delete("/delete_todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,db:db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(401,detail='Invalid User')
    todo_model = db.query(Todos).filter(Todos.id == todo_id and Todos.owner_id == user.get('user_id')).first()
    if todo_model is not None:
        db.delete(todo_model)
        db.commit()
    else:
        raise HTTPException(404,detail='Todo Not Found')