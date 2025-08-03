import boto3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def fetch(region: str):
    """
    Yields one dict per S3 bucket in the given region.
    Note: S3 buckets are global, so we list them all.
    """
    try:
        s3 = boto3.client("s3", region_name=region)
        for b in s3.list_buckets().get("Buckets", []):
            yield {
                "snapshot_time": datetime.utcnow().isoformat(),
                "resource_id": f"arn:aws:s3:::{b['Name']}",
                "resource_type": "s3",
                "properties": {"raw": b},
            }
    except Exception as e:
        logger.warning(f"Failed to fetch S3 buckets: {e}")
        # Return empty list if AWS credentials are not configured or other errors
        return
