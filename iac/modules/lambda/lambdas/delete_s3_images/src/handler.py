import os
import logging
from datetime import datetime, timezone, timedelta

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# S3 client
s3 = boto3.client('s3')

# Environment variables
BUCKET_NAME = os.environ.get("BUCKET_NAME")
PREFIX = os.environ.get("PREFIX", "")  # Optional folder path
TIMEOUT = os.environ.get("TIMEOUT", "30")  # Default timeout in seconds

def main(event, context):
    """Lambda Handler Transformation"""
    delete_s3_images()

def delete_s3_images():
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=TIMEOUT)
    logger.info(f"Starting cleanup for {BUCKET_NAME}/{PREFIX} — removing files older than {cutoff_date.isoformat()}")

    deleted_keys = []
    paginator = s3.get_paginator('list_objects_v2')

    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=PREFIX):
        for obj in page.get("Contents", []):
            key = obj['Key']
            last_modified = obj['LastModified']

            if last_modified < cutoff_date:
                logger.info(f"Deleting file: {key} (last modified: {last_modified})")
                s3.delete_object(Bucket=BUCKET_NAME, Key=key)
                deleted_keys.append(key)

    logger.info(f"Total files deleted: {len(deleted_keys)}")
    
    if deleted_keys:
        logger.info("Deleted file list:")
        for k in deleted_keys:
            logger.info(f"  - {k}")
    else:
        logger.info("No files were deleted during this execution.")
    
    logger.info("Cleanup completed.")