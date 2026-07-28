import logging
import asyncio
from typing import Dict, Any
from google.ads.datamanager_v1 import (
    IngestionServiceClient,
    IngestAudienceMembersRequest,
    Destination,
    ProductAccount,
    AudienceMember,
    UserData,
    UserIdentifier,
    AddressInfo,
    Consent,
    ConsentStatus,
    Encoding,
    TermsOfService,
    TermsOfServiceStatus,
)
from google.oauth2.credentials import Credentials
from google.api_core.exceptions import GoogleAPICallError
from models.google_ads import GoogleAdsBatchPayload
from core.config import settings

logger = logging.getLogger("Audience_Uploader")


def _build_client() -> IngestionServiceClient:
    credentials = Credentials(
        token=None,
        refresh_token=settings.google_ads_refresh_token,
        client_id=settings.google_ads_client_id,
        client_secret=settings.google_ads_client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/datamanager"],
    )
    return IngestionServiceClient(credentials=credentials)


def _build_destination(payload: GoogleAdsBatchPayload) -> Destination:
    destination = Destination(
        operating_account=ProductAccount(
            account_type=ProductAccount.AccountType.GOOGLE_ADS,
            account_id=payload.customer_id,
        ),
        product_destination_id=payload.user_list_id,
    )
    if settings.google_ads_login_customer_id and settings.google_ads_login_customer_id != payload.customer_id:
        destination.login_account = ProductAccount(
            account_type=ProductAccount.AccountType.GOOGLE_ADS,
            account_id=settings.google_ads_login_customer_id,
        )
    return destination


def _build_audience_members(payload: GoogleAdsBatchPayload) -> list[AudienceMember]:
    members = []
    for op in payload.operations:
        identifiers = []
        for identifier in op.user_identifiers:
            if identifier.hashed_email:
                identifiers.append(UserIdentifier(email_address=identifier.hashed_email))
            elif identifier.hashed_phone_number:
                identifiers.append(UserIdentifier(phone_number=identifier.hashed_phone_number))
            # NOTE: address-based identifiers need region_code + postal_code
            # (Data Manager API requirement) which UserIdentifier model
            # doesn't currently capture. Skipping name-only until model
            # is extended and CSV schema provides those fields.
            elif identifier.hashed_first_name:
                logger.warning("Skipping name-only identifier: address_code/postal_code not in model.")
                continue

        if identifiers:
            members.append(AudienceMember(user_data=UserData(user_identifiers=identifiers)))
    return members


def _dispatch_sync(payload: GoogleAdsBatchPayload, request_id: str) -> Dict[str, Any]:
    client = _build_client()
    destination = _build_destination(payload)
    audience_members = _build_audience_members(payload)

    consent_status = ConsentStatus.CONSENT_GRANTED if payload.consent.ad_user_data == "GRANTED" else ConsentStatus.CONSENT_DENIED
    personalization_status = ConsentStatus.CONSENT_GRANTED if payload.consent.ad_personalization == "GRANTED" else ConsentStatus.CONSENT_DENIED

    request = IngestAudienceMembersRequest(
        destinations=[destination],
        audience_members=audience_members,
        consent=Consent(
            ad_user_data=consent_status,
            ad_personalization=personalization_status,
        ),
        validate_only=False,
        encoding=Encoding.HEX,
        terms_of_service=TermsOfService(
            customer_match_terms_of_service_status=TermsOfServiceStatus.ACCEPTED
        ),
    )

    response = client.ingest_audience_members(request=request, timeout=60.0)
    logger.info(f"[{request_id}] Data Manager raw response: {response!r}")
    logger.info(f"[{request_id}] Google Ads Data Manager job accepted, request_id={response.request_id}, operations={len(audience_members)}")
    return {"status": "success", "operations_processed": len(audience_members), "error": None}


async def dispatch_batches_to_google_ads(payload: GoogleAdsBatchPayload, request_id: str) -> Dict[str, Any]:
    try:
        return await asyncio.to_thread(_dispatch_sync, payload, request_id)
    except GoogleAPICallError as ex:
        logger.error(f"[{request_id}] Google Ads Data Manager dispatch failed: {ex}")
        return {"status": "failed", "operations_processed": 0, "error": str(ex)}
    except Exception as ex:
        logger.error(f"[{request_id}] Google Ads Data Manager dispatch unexpected error: {ex!r}")
        return {"status": "failed", "operations_processed": 0, "error": str(ex)}