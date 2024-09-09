# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import base64
import logging
import mimetypes
from io import BytesIO
from typing import Dict, List, Union, Optional

import boto3
import pdfplumber
from PIL import Image

from .image_validator import ImageValidator

logger = logging.getLogger(__name__)


class FileConverter:
    def __init__(self, file_path: str, pages: List[int], s3_client: Optional[boto3.client]):
        """
        Initialize the FileConverter object.

        Args:
            file_path (str): The path to the file (local or S3).
            s3_client (boto3.client, optional): The boto3 S3 client. Defaults to None.
        """
        self.file_path = file_path
        self.s3_client = s3_client
        self.pages = pages
        self.file_bytes, self.mime_type = self._get_file_bytes_and_mime_type()

    def _get_file_bytes_and_mime_type(self) -> tuple[bytes, str]:
        """
        Get the file bytes and MIME type of the file.

        Returns:
            tuple[bytes, str]: A tuple containing the file bytes and MIME type.
        """
        if self.file_path.startswith("s3://"):
            if self.s3_client is None:
                raise ValueError("S3 client is required for S3 file paths")
            bucket_name, key = self._parse_s3_path(self.file_path)
            response = self.s3_client.get_object(Bucket=bucket_name, Key=key)
            file_bytes = response["Body"].read()
        else:
            with open(self.file_path, "rb") as f:
                file_bytes = f.read()

        mime_type = self._get_mime_type(file_bytes)
        return file_bytes, mime_type

    def _get_mime_type(self, file_bytes: bytes) -> str:
        """
        Determine the MIME type of the file based on its contents.

        Args:
            file_bytes (bytes): The file bytes.

        Returns:
            str: The MIME type of the file.

        Raises:
            ValueError: If the file type is not supported.
        """
        mime_type, _ = mimetypes.guess_type(self.file_path)
        if mime_type is None:
            raise ValueError("Unsupported file type")
        return mime_type

    def _parse_s3_path(self, s3_path: str) -> tuple[str, str]:
        """
        Parse the S3 file path and extract the bucket name and key.

        Args:
            s3_path (str): The S3 file path.

        Returns:
            tuple[str, str]: A tuple containing the bucket name and key.
        """
        parts = s3_path[5:].partition("/")
        bucket_name = parts[0]
        key = parts[2]
        return bucket_name, key

    def convert_to_base64(self) -> List[Dict[str, Union[int, str]]]:
        """
        Convert the file to Base64 encoded string(s).

        Returns:
            List[Dict[str, Union[int, str]]]: A list of dictionaries containing the page number and Base64 encoded string.

        Raises:
            RuntimeError: If an error occurs during the file conversion process.
        """
        try:
            if self.mime_type == "image/jpeg" or self.mime_type == "image/png":
                if self.file_path.startswith("s3://"):
                    image_bytes = self.file_bytes
                else:
                    with open(self.file_path, "rb") as f:
                        image_bytes = f.read()
                validator = ImageValidator(image_bytes)
                validator.validate_image()
                base64_string = base64.b64encode(image_bytes).decode("utf-8")
                return [{"page": 1, "base64string": base64_string}]

            elif self.mime_type == "application/pdf":
                with pdfplumber.open(
                    BytesIO(self.file_bytes)
                    if self.file_path.startswith("s3://")
                    else self.file_path
                ) as pdf:
                    base64_strings = []
                    if self.pages == [0]:
                        page_nums = range(min(20, len(pdf.pages)))
                    else:
                        page_nums = [p - 1 for p in self.pages if p <= len(pdf.pages) and p > 0]

                    for page_num in page_nums:
                        page = pdf.pages[page_num]
                        img = page.to_image(resolution=150).original
                        img_bytes = BytesIO()
                        img.save(img_bytes, format="PNG")
                        base64_string = base64.b64encode(img_bytes.getvalue()).decode("utf-8")
                        base64_strings.append({"page": page_num + 1, "base64string": base64_string})
                return base64_strings

            elif self.mime_type == "image/tiff":
                with Image.open(
                    BytesIO(self.file_bytes)
                    if self.file_path.startswith("s3://")
                    else self.file_path
                ) as img:
                    base64_strings = []
                    if self.pages == [0]:
                        frame_nums = range(min(20, img.n_frames))
                    else:
                        frame_nums = [p - 1 for p in self.pages if p <= img.n_frames and p > 0]
                    for i in frame_nums:
                        img.seek(i)
                        img_byte_arr = BytesIO()
                        img.save(img_byte_arr, format="PNG")
                        base64_string = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
                        base64_strings.append({"page": i + 1, "base64string": base64_string})
                return base64_strings
            else:
                logger.error("Unsupported file type")
                raise ValueError("Unsupported file type")
        except Exception as e:
            logger.error(f"Error converting file to Base64: {str(e)}")
            raise RuntimeError(f"Error converting file to Base64: {str(e)}")
