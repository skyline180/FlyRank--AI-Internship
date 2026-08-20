import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Task API", version="2.0", description="A simple CRUD API for managing tasks with SQLite")
DB_FILE = "tasks.db"

class Task(BaseModel):
    title: str
    done: bool = False

class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        if cursor.fetchone()[0] == 0:
            seed_tasks = [
                ("Learn FastAPI", 0), 
                ("Build a CRUD API", 0), 
                ("Deploy to production", 0)
            ]
            cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", seed_tasks)
        conn.commit()

init_db()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row 
    try:
        yield conn
    finally:
        conn.close()

@app.get("/", tags=["Info"])
def root():
    """Get API information"""
    return {
        "name": "Task API",
        "version": "2.0",
        "endpoints": ["/tasks", "/health", "/stats", "/docs"]
    }

@app.get("/health", tags=["Info"])
def health():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None, db: sqlite3.Connection = Depends(get_db)):
    """List all tasks. Optional filters: done=true/false, search=<text>"""
    cursor = db.cursor()
    
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    
    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)
        
    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")
        
    cursor.execute(query, params)
    
    return [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in cursor.fetchall()]

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def get_task(task_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Get a single task by ID"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}