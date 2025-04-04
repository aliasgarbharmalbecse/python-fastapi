from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

#create engine
engine = create_engine(DATABASE_URL, echo=True)

#initiate session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#base class for model
class Base(DeclarativeBase):
    pass


#dependency for db connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
