from sqlalchemy.orm import Session

import models, schemas

def get_hh(hh_id:int
            ,db: Session):
    return db.query(models.HHSummary).filter(models.HHSummary.household_key == hh_id).first()
