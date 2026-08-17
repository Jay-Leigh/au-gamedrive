import logging
from typing import Dict, Any
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from models.google_ads import GoogleAdsBatchPayload
from core.config import settings

def _build_client() -> GoogleAdsClient:
    return GoogleAdsClient.load_from_string(settings.google_ads_yaml)

async def dispatch_batches_to_google_ads(payload: GoogleAdsBatchPayload, request_id: str) -> Dict[str, Any]:
    try:
        client = _build_client()
        service = client.get_service("OfflineUserDataJobService")

        job_operation = client.get_type("OfflineUserDataJob")
        job_operation.type_ = client.enums.OfflineUserDataJobTypeEnum.CUSTOMER_MATCH_USER_LIST
        job_operation.customer_match_user_list_metadata.user_list = f"customers/{payload.customer_id}/userLists/{payload.user_list_id}"
        job_operation.customer_match_user_list_metadata.consent.ad_user_data = client.enums.ConsentStatusEnum[payload.consent.ad_user_data]
        job_operation.customer_match_user_list_metadata.consent.ad_personalization = client.enums.ConsentStatusEnum[payload.consent.ad_personalization]

        create_response = service.create_offline_user_data_job(customer_id=payload.customer_id, job=job_operation)
        job_resource_name = create_response.resource_name

        operations = []
        for op in payload.operations:
            add_op = client.get_type("OfflineUserDataJobOperation")
            user_data = add_op.create
            for identifier in op.user_identifiers:
                ui = client.get_type("UserIdentifier")
                if identifier.hashed_email:
                    ui.hashed_email = identifier.hashed_email
                elif identifier.hashed_phone_number:
                    ui.hashed_phone_number = identifier.hashed_phone_number
                elif identifier.hashed_first_name:
                    ui.address_info.hashed_first_name = identifier.hashed_first_name
                    if identifier.hashed_last_name:
                        ui.address_info.hashed_last_name = identifier.hashed_last_name
                user_data.user_identifiers.append(ui)
            operations.append(add_op)

        service.add_offline_user_data_job_operations(resource_name=job_resource_name, operations=operations, enable_partial_failure=True)
        service.run_offline_user_data_job(resource_name=job_resource_name)

        logging.info(f"[{request_id}] Google Ads job {job_resource_name} submitted, {len(operations)} operations.")
        return {"status": "success", "operations_processed": len(operations), "error": None}

    except GoogleAdsException as ex:
        errors = "; ".join(e.message for e in ex.failure.errors)
        logging.error(f"[{request_id}] Google Ads dispatch failed: {errors}")
        return {"status": "failed", "operations_processed": 0, "error": errors}