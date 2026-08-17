# services/approved_accounts.py
from typing import Optional
from sqlalchemy.orm import Session
from db.models import ApprovedAccount

def is_known_account(db: Session, account: str) -> bool:
    return db.query(ApprovedAccount).filter_by(account=account, is_active=True).first() is not None

def get_destination(db: Session, account: str, audience_name: str, platform: str) -> Optional[dict]:
    row = db.query(ApprovedAccount).filter_by(account=account, audience_name=audience_name, platform=platform, is_active=True).first()
    return row.destination if row else None

def upsert_approved_account(db: Session, account: str, audience_name: str, platform: str, destination: dict, is_active: bool = True):
    row = db.query(ApprovedAccount).filter_by(account=account, audience_name=audience_name, platform=platform).first()
    if row:
        row.destination, row.is_active = destination, is_active
    else:
        row = ApprovedAccount(account=account, audience_name=audience_name, platform=platform, destination=destination, is_active=is_active)
        db.add(row)
    db.commit()
    return row