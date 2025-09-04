# --------------------------
# IMPORTS
# --------------------------
from fastapi import FastAPI, Depends  # FastAPI framework + helper for database sessions
from sqlalchemy.orm import Session     # Workspace to interact with the database
from database import SessionLocal, engine, Base  # DB connection, session factory, and base class
import models                          # Our Task model
from pydantic import BaseModel         # Data validation for incoming requests
from typing import Optional             # To make some fields in table optional
from datetime import date               # To handle due dates

# --------------------------
# DATABASE SETUP
# --------------------------
Base.metadata.create_all(bind=engine)  # Create tables in the database if they don't exist

# --------------------------
# INITIALIZE FASTAPI
# --------------------------
app = FastAPI()  # Create the FastAPI app object

# --------------------------
# DATABASE SESSION DEPENDENCY
# --------------------------
def get_db():
    """
    This function gives a session (workspace) to each route.
    'yield db' hands the session to the route,
    and 'db.close()' ensures it's closed after the route finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------
# Pydantic SCHEMA FOR TASKS
# --------------------------
class TaskCreate(BaseModel):
    """
    This is a blueprint for incoming data when someone wants to create a task.
    Ensures data matches these rules before inserting into the database.
    """
    title: str                     # Required: Task title
    assigned_to: Optional[str] = None  # Optional: Person assigned to task
    status: Optional[str] = None       # Optional: Task status
    due_date: Optional[date] = None    # Optional: Due date

# --------------------------
# API ROUTES
# --------------------------
@app.post("/tasks/")  # When a POST request is made to /tasks/
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    This route creates a new task in the database.
    Steps:
    1. Convert incoming data into a Task model object
    2. Add it to the session (workspace)
    3. Commit it (save to DB)
    4. Refresh to get the new ID from DB
    5. Return the new task
    """
    db_task = models.Task(**task.dict())  # Create a Task object from incoming data
    db.add(db_task)                        # Stage it in the workspace
    db.commit()                            # Save it to the database
    db.refresh(db_task)                    # Get updated data (like auto-generated ID)
    return db_task                         # Send back the task as response
