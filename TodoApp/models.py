from database import Base
from sqlalchemy import Column, INTEGER, String, Boolean

class Todos(Base):
    __tablename__ = 'todos'

    id = Column(INTEGER,primary_key=True,index=True)
    title = Column(String)
    desc = Column(String)
    priority = Column(String)
    progress = Column(Boolean,default=False)