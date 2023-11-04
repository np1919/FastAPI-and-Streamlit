from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from my_url import _SQLALCHEMY_DATABASE_URL

engine = create_engine(
_SQLALCHEMY_DATABASE_URL,
echo=True,
connect_args={"check_same_thread": False}
)

# connect args for sqlite3 db
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.commit()
        db.close()


