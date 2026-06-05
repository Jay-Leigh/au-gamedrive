# db/seed.py  ← run this once to populate the test DB
from db.database import engine, SessionLocal
from db.models import ApprovedAccount, Base

def seed():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    accounts = [
        ApprovedAccount(
            account_name="realbeds",
            meta_audience_id="YOUR_META_AUDIENCE_ID",
            google_customer_id="123-456-7890",
            google_user_list_id="987654321"
        ),
        ApprovedAccount(
            account_name="africanoverlandtours",
            meta_audience_id="YOUR_META_AUDIENCE_ID_2",
            google_customer_id="111-222-3333",
            google_user_list_id="444555666"
        ),
    ]

    for account in accounts:
        existing = db.query(ApprovedAccount).filter_by(account_name=account.account_name).first()
        if not existing:
            db.add(account)

    db.commit()
    db.close()
    print("✅ Test DB seeded successfully")


if __name__ == "__main__":
    seed()