import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '..', 'kraken.db')

engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    module = Column(String, index=True)
    target = Column(String, index=True)
    username = Column(String)
    password = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
