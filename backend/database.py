from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# SQLite URL 설정 (파일 기반)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./localhub.db")

# SQLite 스레드 제약 완화 설정
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# DB 세션 의존성 주입 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()