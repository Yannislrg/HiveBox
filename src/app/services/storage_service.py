import json
import logging
import os
from datetime import datetime, timezone
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio-infra.minio.svc.cluster.local:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "hivebox-data")

class StorageService:
    """Service to handle data persistence in S3-compatible storage."""
    def __init__(self):
        self._s3 = None
        self._bucket_checked = False

    @property
    def s3(self):
        if self._s3 is None:
            self._s3 = boto3.client(
                's3',
                endpoint_url=MINIO_ENDPOINT,
                aws_access_key_id=MINIO_ACCESS_KEY,
                aws_secret_access_key=MINIO_SECRET_KEY,
                config=Config(signature_version='s3v4'),
                region_name='us-east-1'
            )
        return self._s3

    def _ensure_bucket_exists(self):
        """Create the bucket if it does not already exist."""
        if self._bucket_checked:
            return
        try:
            self.s3.head_bucket(Bucket=MINIO_BUCKET)
            self._bucket_checked = True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.info(f"Bucket {MINIO_BUCKET} does not exist. Creating it.")
                self.s3.create_bucket(Bucket=MINIO_BUCKET)
                self._bucket_checked = True
            else:
                logger.error(f"Failed to check bucket existence: {e}")
                raise e

    def store_data(self, data: dict):
        """Store the provided data in MinIO as a JSON file."""
        self._ensure_bucket_exists()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"sensor_data_{timestamp}.json"
        
        try:
            self.s3.put_object(
                Bucket=MINIO_BUCKET,
                Key=filename,
                Body=json.dumps(data, indent=2),
                ContentType='application/json'
            )
            logger.info(f"Successfully stored data in {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to store data in MinIO: {e}")
            raise e

storage_service = StorageService()
