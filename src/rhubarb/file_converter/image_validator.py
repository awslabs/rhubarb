# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import io
import logging
from typing import Tuple

from PIL import Image

logger = logging.getLogger(__name__)


class ImageValidator:
    def __init__(self, file_bytes: bytes):
        self.file_bytes = file_bytes

    def _get_image_size_and_format(self) -> Tuple[int, str]:
        """
        Get the size (in bytes) and format of the image file.

        Returns:
            Tuple[int, str]: A tuple containing the file size and format.
        """
        image = Image.open(io.BytesIO(self.file_bytes))
        file_size = len(self.file_bytes)
        file_format = image.format.lower()
        return file_size, file_format

    def validate_image(self) -> bool:
        """
        Validate the image file based on the specified criteria.

        Returns:
            bool: True if the image file meets the criteria, False otherwise.

        Raises:
            ValueError: If the file format is not supported or the file size exceeds the maximum allowed limit.
        """
        file_size, file_format = self._get_image_size_and_format()

        if file_format not in ["jpeg", "png"]:
            logger.error(f"Unsupported file format: {file_format}")
            raise ValueError(f"Unsupported file format: {file_format}")

        if file_size > 5 * 1024 * 1024:  # 5 MB
            logger.error("File size exceeds the maximum allowed limit of 5 MB")
            raise ValueError("File size exceeds the maximum allowed limit of 5 MB")

        return True
