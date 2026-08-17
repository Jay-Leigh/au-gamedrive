import asyncio
import hashlib
from models.google_ads import GoogleAdsBatchPayload, UserData, UserIdentifier, Consent
from clients.google_ads_client import dispatch_batches_to_google_ads


def sha256(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()


async def main():
    payload = GoogleAdsBatchPayload(
        customer_id="7092652546",
        user_list_id="9425866437",
        operations=[
            UserData(user_identifiers=[
                UserIdentifier(hashed_email=sha256("test@example.com")),
            ]),
        ],
        consent=Consent(ad_user_data="GRANTED", ad_personalization="GRANTED"),
    )

    result = await dispatch_batches_to_google_ads(payload, request_id="cli-test-001")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())