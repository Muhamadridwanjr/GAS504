"""
S3/MinIO upload client.
"""
from __future__ import annotations

from pathlib import Path

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


class S3Client:
    """Upload files to MinIO/S3-compatible storage."""

    def __init__(self):
        self.bucket = settings.S3_BUCKET
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=BotoConfig(signature_version="s3v4"),
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Create bucket if it doesn't exist."""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            logger.info("Creating bucket %s", self.bucket)
            try:
                self.client.create_bucket(Bucket=self.bucket)
            except ClientError as e:
                logger.error("Failed to create bucket: %s", e)

    def upload_file(self, local_path: Path, s3_key: str) -> bool:
        """
        Upload a single file to S3.

        Args:
            local_path: Local file to upload.
            s3_key: S3 object key (path in bucket).

        Returns:
            True if successful.
        """
        try:
            self.client.upload_file(str(local_path), self.bucket, s3_key)
            logger.info("Uploaded %s → s3://%s/%s", local_path.name, self.bucket, s3_key)
            return True
        except ClientError as e:
            logger.error("Upload failed for %s: %s", s3_key, e)
            return False

    def upload_partitions(self, files: list[Path], base_dir: str) -> int:
        """
        Upload a list of partitioned parquet files to S3.

        Files are expected to be under base_dir; the relative path
        structure is preserved in S3.
        """
        success = 0
        base = Path(base_dir)
        for f in files:
            try:
                rel = f.relative_to(base)
            except ValueError:
                rel = Path(f.name)
            s3_key = str(rel)
            if self.upload_file(f, s3_key):
                success += 1
        logger.info("Uploaded %d / %d files", success, len(files))
        return success

    def file_exists(self, s3_key: str) -> bool:
        """Check if an object already exists in S3."""
        try:
            self.client.head_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError:
            return False
