from sqlalchemy import Column, Integer, String, Date
from database import Base

class Task(Base):
    __tablename__ = "tasks" # This is the exact table name in PostgreSQL. We want all of our columns to match the tables we create in PostgreSQL.

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    assigned_to = Column(String, nullable=True)
    status = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
