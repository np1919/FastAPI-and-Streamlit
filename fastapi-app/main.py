from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine

#models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home_page():
    return "Hello World"

@app.get("/hh/{hh_id}", response_model=schemas.HHSummary)
def read_hh(hh_id: int, db: Session = Depends(get_db)):
    '''return the row from HHSummary related to `hh_id`. 
    this input to be selected by -- and output to be parsed by -- streamlit frontend app'''
    hh = crud.get_hh(hh_id=hh_id, db=db)
    if hh is None:
        raise HTTPException(status_code=404, detail="Household not found")
    return hh
