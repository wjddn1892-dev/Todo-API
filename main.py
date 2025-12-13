from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import database, models
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()

# 데이터베이스와 연결 설정
database.Base.metadata.create_all(bind=database.engine)

# JWT 설정
SECRET_KEY = "my-secret-key"  # 실제로는 환경변수로 관리
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

def get_password_hash(password):
    return bcrypt_context.hash(password)

# 비밀번호 검증 함수
def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

# 토큰 생성 함수
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

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

class User(BaseModel):    # 회원가입 모델
    username: str
    email: str
    password: str


# 유저 생성
@app.post("/users/register")
def create_new_user(user: User, db: Session = Depends(get_db)):
    create_user = models.User()
    create_user.username = user.username
    create_user.email = user.email
    create_user.hashed_password = get_password_hash(user.password)
    db.add(create_user)
    db.commit()
    db.refresh(create_user)
    return create_user

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. DB에서 username으로 사용자 조회
    # 2. 사용자 없으면 401 에러
    # 3. 비밀번호 검증 (verify_password 사용)
    # 4. 검증 실패하면 401 에러
    # 5. 토큰 생성 (create_access_token 사용)
    # 6. {"access_token": token, "token_type": "bearer"} 반환
    
    # 사용자 조회
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    # 비밀번호 검증
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 토큰 생성
    access_token = create_access_token(user.username, user_id=user.id, expires_delta=expires_delta)
    return {"access_token": access_token, "token_type": "bearer"}


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
    
