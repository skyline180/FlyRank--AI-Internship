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