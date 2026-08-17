from google.ads.datamanager_v1 import (
    IngestionServiceClient,
    IngestEventsRequest,
    Destination,
    ProductAccount,
    Event,
    AdIdentifiers,
    UserData,
    UserIdentifier,
    Consent,
    ConsentStatus,
    Encoding,
    EventSource,
)
from google.oauth2.credentials import Credentials
from google.api_core.exceptions import GoogleAPICallError
from models.datamanager_schema import GoogleAdsConversion
from config import config
import logging
import asyncio

logger = logging.getLogger("Offline_Conversions")


class DataManagerAPIClient:
    def __init__(self):

        self.credentials = Credentials(
            token=None,
            refresh_token=config.google_ads_refresh_token,
            client_id=config.google_ads_client_id,
            client_secret=config.google_ads_client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=["https://www.googleapis.com/auth/datamanager"],
        )
        self.client = IngestionServiceClient(credentials=self.credentials)

        self.customer_id = config.google_ads_customer_id
        self.login_customer_id = config.google_ads_login_customer_id

    async def upload_conversions_async(self, conversions: list[GoogleAdsConversion]):
        """Wraps the synchronous Data Manager gRPC call in a worker thread."""
        if not conversions:
            return

        await asyncio.to_thread(self._upload_batches, conversions)

    def _build_destination(self, conversion_action_ref: str) -> Destination:
        conversion_action_id = conversion_action_ref.rsplit("/", 1)[-1]

        destination = Destination(
            operating_account=ProductAccount(
                account_type=ProductAccount.AccountType.GOOGLE_ADS,
                account_id=self.customer_id,
            ),
            product_destination_id=conversion_action_id,
        )
        if self.login_customer_id and self.login_customer_id != self.customer_id:
            destination.login_account = ProductAccount(
                account_type=ProductAccount.AccountType.GOOGLE_ADS,
                account_id=self.login_customer_id,
            )
        return destination

    def _build_event(self, conv: GoogleAdsConversion) -> Event:
        event = Event(
            event_timestamp=conv.conversion_date_time, 
            transaction_id=conv.order_id,
            event_source=EventSource.OTHER,  
            currency=conv.currency_code,
            conversion_value=conv.conversion_value,
        )

        if conv.gclid:
            event.ad_identifiers = AdIdentifiers(gclid=conv.gclid)

        user_identifiers = []
        if conv.hashed_email:
            user_identifiers.append(UserIdentifier(email_address=conv.hashed_email))
        if conv.hashed_phone:
            user_identifiers.append(UserIdentifier(phone_number=conv.hashed_phone))

        if user_identifiers:
            event.user_data = UserData(user_identifiers=user_identifiers)

        return event

    def _upload_batches(self, conversions: list[GoogleAdsConversion]):
        """Builds payloads and ingests in batches of 2000 (Data Manager API max per request)."""
        batch_size = 2000

        for i in range(0, len(conversions), batch_size):
            batch = conversions[i:i + batch_size]
            destination = self._build_destination(batch[0].conversion_action)
            events = [self._build_event(conv) for conv in batch]

            request = IngestEventsRequest(
                destinations=[destination],
                events=events,
                consent=Consent(
                    ad_user_data=ConsentStatus.CONSENT_GRANTED,
                    ad_personalization=ConsentStatus.CONSENT_GRANTED,
                ),
                validate_only=False,
                encoding=Encoding.HEX,
            )

            try:
                response = self.client.ingest_events(request=request)
                logger.info(f"Ingested batch, request_id={response.request_id}")
            except GoogleAPICallError as ex:
                logger.error(f"Data Manager API error: {ex}")
                raise