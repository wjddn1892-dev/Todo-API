from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(DATABASE_URL)    # 데이터베이스 엔진 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)    # 세션 생성
"""
  - DB 작업(CRUD)을 할 때 사용하는 세션 생성기
  - SessionLocal()을 호출하면 새 세션이 만들어짐
  - autocommit=False: 명시적으로 commit 해야 저장됨, 이를 위해 False로 설정
  - autoflush=False: 자동으로 DB에 반영하지 않음
"""

Base = declarative_base()    # 모델 기반 클래스 생성
"""
  - 모든 DB 모델이 상속받을 부모 클래스
  - 이걸 상속받아야 SQLAlchemy가 "이건 DB 테이블이다"라고 인식함
"""