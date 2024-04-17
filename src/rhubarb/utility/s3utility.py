# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, Tuple, Optional

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class S3Utility:
    def __init__(self, s3_client: Any) -> None:
        self.s3_client = s3_client

    def read_file(self, s3_path: str) -> Optional[bytes]:
        """Reads a file from S3 and returns its bytes."""
        bucket_name, object_key = self._parse_s3_path(s3_path)
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Failed to read file {s3_path}: {e}")
            raise e

    def save_file(self, s3_path: str, data: bytes) -> None:
        """Saves data to a file in S3."""
        bucket_name, object_key = self._parse_s3_path(s3_path)
        try:
            self.s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=data)            
        except ClientError as e:
            logger.error(f"Failed to save file {s3_path}: {e}")
            raise e

    def upload_file(self, local_path: str, s3_path: str) -> None:
        """Uploads a local file to S3."""
        bucket_name, object_key = self._parse_s3_path(s3_path)
        try:
            self.s3_client.upload_file(local_path, bucket_name, object_key)            
        except ClientError as e:
            logger.error(f"Failed to upload file {local_path} to {s3_path}: {e}")
            raise e

    def delete_file(self, s3_path: str) -> None:
        """Deletes a file from S3."""
        bucket_name, object_key = self._parse_s3_path(s3_path)
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_key)            
        except ClientError as e:
            logger.error(f"Failed to delete file {s3_path}: {e}")
            raise e

    def check_file_exists(self, s3_path: str) -> bool:
        """Checks the existence of a file in S3."""
        bucket_name, object_key = self._parse_s3_path(s3_path)
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=object_key)
            return True
        except ClientError as e:
            logger.error("File does not exists")
            raise e

    def _parse_s3_path(self, s3_path: str) -> Tuple[str, str]:
        """Helper method to extract bucket name and object key from an S3 path."""
        if not s3_path.startswith("s3://"):
            raise ValueError("Invalid S3 path.")
        parts = s3_path.replace("s3://", "").split("/", 1)
        return parts[0], parts[1]