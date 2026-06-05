# db/models.py
from sqlalchemy import Column, String, JSON
from db.database import Base 

class ApprovedAccount(Base):
    __tablename__ = "approved_accounts"

    account_name = Column(String, primary_key=True, index=True)
    meta_audience_id = Column(String, nullable=True)   # JSONB in Postgres for multiple audiences
    google_customer_id = Column(String, nullable=True)
    google_user_list_id = Column(String, nullable=True)

class 