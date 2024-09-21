from TodoApp.database import Base
from sqlalchemy import Column, INTEGER, String, Boolean, ForeignKey


class Users(Base):
    __tablename__ = 'users'
    id = Column(INTEGER,primary_key=True,index=True)
    username = Column(String, unique=True)
    fname = Column(String)
    lname = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)

class Todos(Base):
    __tablename__ = 'todos'

    id = Column(INTEGER,primary_key=True,index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(INTEGER)
    progress = Column(Boolean,default=False)
    owner_id = Column(INTEGER, ForeignKey("users.id"))