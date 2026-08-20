from fastapi import FastAPI, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from typing import Optional

app = FastAPI(title="Task API", version="1.0", description="A simple CRUD API for managing tasks")

class Task(BaseModel):
    title: str
    done: bool = False

class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool

# In-memory DB
tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Deploy to production", "done": False},
]

next_id = 4


@app.get("/", tags=["Info"])
def root():
    """Get API information"""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/health", "/stats", "/docs"]
    }

@app.get("/health", tags=["Info"])
def health():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/tasks", response_model=list[TaskResponse], tags=["Tasks"])
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    """List all tasks. Optional filters: done=true/false, search=<text>"""
    filtered = tasks
    
    if done is not None:
        filtered = [t for t in filtered if t["done"] == done]
    
    if search:
        filtered = [t for t in filtered if search.lower() in t["title"].lower()]
    
    return filtered

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def get_task(task_id: int):
    """Get a single task by ID"""
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.post("/tasks", response_model=TaskResponse, status_code=201, tags=["Tasks"])
def create_task(task: Task):
    """Create a new task"""
    global next_id
    
    # Validate input
    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="title is required and cannot be empty"
        )
    
    new_task = {
        "id": next_id,
        "title": task.title.strip(),
        "done": task.done
    }
    tasks.append(new_task)
    next_id += 1
    
    return new_task


@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def update_task(task_id: int, task: Task):
    """Update a task's title and/or done status"""
    # Validate input
    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="title is required and cannot be empty"
        )
    
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks[i]["title"] = task.title.strip()
            tasks[i]["done"] = task.done
            return tasks[i]
    
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=204, tags=["Tasks"])
def delete_task(task_id: int):
    """Delete a task"""
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.get("/stats", tags=["Info"])
def get_stats():
    """Get task statistics"""
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    open_count = total - done
    
    return {
        "total": total,
        "done": done,
        "open": open_count
    }

@app.post("/reset", tags=["Maintenance"])
def reset_tasks():
    """Reset tasks to initial state (useful for testing)"""
    global tasks, next_id
    tasks = [
        {"id": 1, "title": "Learn FastAPI", "done": False},
        {"id": 2, "title": "Build a CRUD API", "done": False},
        {"id": 3, "title": "Deploy to production", "done": False},
    ]
    next_id = 4
    return {"status": "reset", "tasks": tasks}