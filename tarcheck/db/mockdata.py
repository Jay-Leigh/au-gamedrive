# db/mockdata.py
from db.database import engine, SessionLocal, Base
import db.models, models.logging
from services.approved_accounts import upsert_approved_account

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    upsert_approved_account(db, "realbeds", "QualifiedLead", "meta", {"audience_id": "120253772920450348"})
    upsert_approved_account(db, "realbeds", "QualifiedLead", "googleads", {"customer_id": "7092652546", "user_list_id": "9425866437"})
    db.close()
    print("seeded")

if __name__ == "__main__":
    seed()