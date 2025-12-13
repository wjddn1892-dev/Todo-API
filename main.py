from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from . import database, models

app = FastAPI()

# 데이터베이스와 연결 설정
models.Base.metadata.create_all(bind=database.engine)

next_id = 0
todo_list = []

class TodoCreate(BaseModel):    # 입력용 모델
    title: str
    completed: bool = False

class Todo(BaseModel):    # 저장용 모델
    id: int
    title: str
    completed: bool

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/todos")
def get_todos():
    return todo_list

@app.post("/todos")
def create_todo(todo: TodoCreate):
    global next_id
    new_todo = Todo(id=next_id, title=todo.title, completed=todo.completed)
    todo_list.append(new_todo.model_dump()) # Convert the Todo object to a dictionary and add it to the todo_list
    next_id += 1
    return new_todo.model_dump()

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    for todo in todo_list:
        if todo["id"] == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: Todo):
    for existing_todo in todo_list:
        if existing_todo["id"] == todo_id:
            existing_todo["title"] = todo.title
            existing_todo["completed"] = todo.completed
            return existing_todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for todo in todo_list:
        if todo["id"] == todo_id:
            todo_list.remove(todo)
            return {"message": "Todo deleted"}
    raise HTTPException(status_code=404, detail="Todo not found")