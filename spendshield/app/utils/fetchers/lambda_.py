import boto3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def fetch(region: str):
    """
    Yields one dict per Lambda function in the given region.
    """
    try:
        lam = boto3.client("lambda", region_name=region)
        paginator = lam.get_paginator("list_functions")
        for page in paginator.paginate():
            for fn in page.get("Functions", []):
                yield {
                    "snapshot_time": datetime.utcnow().isoformat(),
                    "resource_id": fn["FunctionArn"],
                    "resource_type": "lambda",
                    "properties": {"raw": fn},
                }
    except Exception as e:
        logger.warning(f"Failed to fetch Lambda functions: {e}")
        # Return empty list if AWS credentials are not configured or other errors
        return
