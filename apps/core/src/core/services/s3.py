import hashlib
import logging
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError
from core.core.config import settings
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self) -> None:
        """Initialize the S3 client."""
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

    def upload_file(
        self, file_content: BinaryIO, bucket_name: str, s3_key: str, content_type: str
    ) -> str:
        """Uploads a file to S3."""
        try:
            self.s3_client.upload_fileobj(
                file_content,
                bucket_name,
                s3_key,
                ExtraArgs={"ContentType": content_type},
            )
            return f"s3://{bucket_name}/{s3_key}"
        except ClientError as e:
            logger.error(
                f"S3 upload failed for bucket {bucket_name}, key {s3_key}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to S3 bucket '{bucket_name}': {e}",
            )

    def get_file_url(self, bucket_name: str, s3_key: str) -> str:
        """Generates a pre-signed URL for a file in S3."""
        try:
            response = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": bucket_name,
                    "Key": s3_key,
                },  # Use the passed bucket_name here
                ExpiresIn=3600,  # URL valid for 1 hour
            )
            return response
        except ClientError as e:
            logger.error(
                f"S3 get file URL failed for bucket {bucket_name}, key {s3_key}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get S3 file URL from bucket '{bucket_name}': {e}",
            )

    def delete_file(self, bucket_name: str, s3_key: str) -> None:
        """Deletes a file from S3."""
        try:
            self.s3_client.delete_object(
                Bucket=bucket_name, Key=s3_key
            )  # Use the passed bucket_name here
        except ClientError as e:
            logger.error(
                f"S3 delete failed for bucket {bucket_name}, key {s3_key}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file from S3 bucket '{bucket_name}': {e}",
            )

    @staticmethod
    def calculate_sha256(file_content: bytes) -> str:
        """Calculates the SHA256 hash of file content."""
        return hashlib.sha256(file_content).hexdigest()


s3_service = S3Service()
