from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import database, models
from sqlalchemy.orm import Session

app = FastAPI()

# 데이터베이스와 연결 설정
database.Base.metadata.create_all(bind=database.engine)

# 의존성 주입: 요청마다 데이터베이스 세션을 생성
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
def get_todos(db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all() # 전체 조회
    return todos

@app.post("/todos")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    new_todo = models.Todo(title=todo.title, completed=todo.completed)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first() # ID로 조회
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    existing_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if existing_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    existing_todo.title = todo.title
    existing_todo.completed = todo.completed
    db.commit()
    db.refresh(existing_todo)
    return existing_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted"}
    
