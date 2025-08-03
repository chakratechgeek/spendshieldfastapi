# app/api/v1/inventory.py

import logging
from fastapi import APIRouter, HTTPException
from app.utils.inventory import fetch_all_resources
from app.utils.aws_storage import upload_resources_to_s3

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/inventory/", response_model=list[dict])
def list_inventory():
    """
    Fetch all AWS resources and persist a snapshot to S3
    in production‐grade folders, then return the data.
    """
    # 1️⃣ Fetch everything
    resources = list(fetch_all_resources())

    if not resources:
        raise HTTPException(status_code=204, detail="No resources found")

    # 2️⃣ Upload to S3
    try:
        key = upload_resources_to_s3(resources)
        logger.info(f"Uploaded snapshot to S3: {key}")
    except ValueError as e:
        # AWS credentials not configured
        logger.warning(f"S3 upload skipped: {e}")
    except Exception as e:
        # Other S3 upload errors - don't block the API
        logger.error(f"S3 upload failed: {e}")

    # 3️⃣ Return the live data
    return resources
