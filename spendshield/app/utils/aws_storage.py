# app/utils/aws_storage.py

import os
import json
import logging
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)

# Pick these up from env in prod  
BUCKET = os.getenv("DISCOVERY_BUCKET", "statefile-chaks")  # Use your existing bucket
PREFIX = os.getenv("DISCOVERY_PREFIX", "spendshield/discovery")

def upload_resources_to_s3(resources: list[dict]) -> str:
    """
    Ensure the S3 bucket exists, then upload the given list of
    resource dicts as newline-delimited JSON into a Hive-style
    partitioned path. Returns the S3 key.
    """
    now = datetime.utcnow()
    # Hive-style partition path
    partition = (
        f"{PREFIX}/"
        f"year={now.year}/"
        f"month={now.month:02d}/"
        f"day={now.day:02d}/"
        f"hour={now.hour:02d}/"
        f"minute={now.minute:02d}"
    )
    filename = f"resource_snapshot_{now.strftime('%Y%m%d_%H%M%S')}.json"
    key = f"{partition}/{filename}"

    s3 = boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key
    )
    
    # Check if AWS credentials are available
    if not settings.aws_access_key_id or not settings.aws_secret_access_key:
        raise ValueError("AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
    
    logger.info(f"Attempting to upload {len(resources)} resources to s3://{BUCKET}/{key}")
    
    # 1️⃣ Ensure bucket exists
    try:
        s3.head_bucket(Bucket=BUCKET)
    except ClientError as e:
        err_code = e.response["Error"].get("Code", "")
        # If bucket truly does not exist, create it
        if err_code in ("404", "NoSuchBucket"):
            create_kwargs = {"Bucket": BUCKET}
            # For non-us-east-1, you must specify LocationConstraint
            if settings.aws_region != "us-east-1":
                create_kwargs["CreateBucketConfiguration"] = {
                    "LocationConstraint": settings.aws_region
                }
            s3.create_bucket(**create_kwargs)
            # wait until it's actually there
            waiter = s3.get_waiter("bucket_exists")
            waiter.wait(Bucket=BUCKET)
        else:
            # Some other error (403, etc.) – re-raise
            raise

    # 2️⃣ Serialize to newline-delimited JSON
    payload = "\n".join(json.dumps(item, default=str) for item in resources)

    # 3️⃣ Upload (with AES256 encryption)
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=payload,
        ServerSideEncryption="AES256",
        ContentType="application/x-ndjson"
    )

    logger.info(f"Successfully uploaded to s3://{BUCKET}/{key}")
    return key
