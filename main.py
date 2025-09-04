# --------------------------
# IMPORTS
# --------------------------
from fastapi import FastAPI, Depends, HTTPException  # FastAPI framework + helper for database sessions, and error handling
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
@app.post("/tasks/")  # When a POST request is made to /tasks/ and no /tasks/{task_id} because we are creating a new task
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

@app.get("/tasks/") #There is no tast_id parameter here because we are fetching all tasks
def get_tasks(db: Session = Depends(get_db)):
    """
    This route fetches all tasks from the database.
    Steps:
    1. Query the Task table for all Task records
    2. Return the list of tasks as JSON
    """
    tasks = db.query(models.Task).all() # Get all tasks from the DB
    return tasks # Return the list of tasks back to client


class TaskUpdate(BaseModel):
    #This blueprint allows updating any subset of task fields.
    # # All fields are optional, so only the fields provided will be changed.

    title: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None


@app.put("/tasks/{task_id}") # When a PUT request is made to /tasks/{task_id} to update a specific task
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """
    This route updates an existing task in the database.
    Steps:
    1. Find the task by ID
    2. If not found, return an error
    3. Update the task fields with incoming data
    4. Commit the changes to the database
    5. Return the updated task
    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first() # Find the task by ID
    if not db_task:
        return HTTPException(status_code=404, detail ="Task not found") # If task not found, return 404 error
    
    update_data = task.dict(exclude_unset=True) # Get only the fields that were provided
    for key, value in update_data.items():
        setattr(db_task, key, value) #Update fields dynamically

    db.commit() # Save changes to the database
    db.refresh(db_task) # Get updated data
    return db_task # Return the updated task
    


@app.delete("/tasks/{task_id}") # When a DELETE request is made to /tasks/{task_id} to delete a specific task
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    This route deletes a task from the database.
    Steps:
    1. Find the task by ID
    2. If not found, return an error
    3. Delete the task from the session (workspace)
    4. Commit the change to the database
    5. Return a success message
    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return HTTPException(status_code=404, detail ="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": f"Task {task_id} deleted successfully"}
# --------------------------

