import boto3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def fetch(region: str):
    try:
        ec2 = boto3.client("ec2", region_name=region)
        for res in ec2.describe_instances()["Reservations"]:
            for inst in res["Instances"]:
                yield {
                    "snapshot_time": datetime.utcnow().isoformat(),
                    "resource_id": inst["InstanceId"],
                    "resource_type": "ec2",
                    "properties": {"raw": inst},
                }
    except Exception as e:
        logger.warning(f"Failed to fetch EC2 instances: {e}")
        # Return empty list if AWS credentials are not configured or other errors
        return
