import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass

# Çevre değişkeninden DATABASE_URL al (Docker/PostgreSQL için), yoksa SQLite kullan
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clinicflow.db")

# SQLite için thread kontrolü, PostgreSQL için boş argüman
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
