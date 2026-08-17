# db/models.py
from sqlalchemy import Column, Integer, String, JSON, Boolean, UniqueConstraint
from db.database import Base

class ApprovedAccount(Base):
    __tablename__ = "approved_accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String, nullable=False, index=True)
    audience_name = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    destination = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    __table_args__ = (UniqueConstraint("account", "audience_name", "platform", name="uq_account_audience_platform"),)

class BatchRegistration(Base):
    __tablename__ = "batch_registrations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String, nullable=False, index=True)
    batch_id = Column(String, nullable=False)
    request_id = Column(String, nullable=False)
    __table_args__ = (UniqueConstraint("account", "batch_id", name="uq_account_batch"),)