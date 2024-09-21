from fastapi import FastAPI,Request
from TodoApp import models
from TodoApp.routers import auth, todos, admin, Users
from TodoApp.database import engine
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

#instance of fastapi
app = FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory='TodoApp/templates')

app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")
#imports our static files before rendering the page

@app.get("/")
def test(request:Request):
    return templates.TemplateResponse("home.html",{"request":request})

# includes the endpoints written in auth.py,todos.py
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(Users.router)
