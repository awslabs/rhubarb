# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from io import BytesIO
from typing import Any, Dict, List, Union, Optional

import pdfplumber
from PIL import Image

from .file_converter import FileConverter

logger = logging.getLogger(__name__)


class LargeDocumentProcessor:
    """
    A class to process large documents that exceed Claude's 20-page limit using a sliding window approach.

    This class handles documents with more than 20 pages by processing them in chunks and
    providing methods to navigate through the document.
    """

    def __init__(self, file_path: str, s3_client: Optional[Any] = None):
        """
        Initialize the LargeDocumentProcessor.

        Args:
            file_path (str): The path to the file (local or S3).
            s3_client (boto3.client, optional): The boto3 S3 client. Defaults to None.
        """
        self.file_path = file_path
        self.s3_client = s3_client
        self.total_pages = self._get_total_pages()
        self.window_size = 20  # Claude's maximum page limit
        self.current_window_start = 1  # Start with the first page

    def _get_total_pages(self) -> int:
        """
        Get the total number of pages in the document.

        Returns:
            int: The total number of pages.
        """
        # Create a temporary FileConverter to get file bytes and mime type
        temp_converter = FileConverter(
            file_path=self.file_path, pages=[0], s3_client=self.s3_client
        )
        file_bytes = temp_converter.file_bytes
        mime_type = temp_converter.mime_type

        if mime_type == "application/pdf":
            with pdfplumber.open(
                BytesIO(file_bytes) if self.file_path.startswith("s3://") else self.file_path
            ) as pdf:
                return len(pdf.pages)
        elif mime_type == "image/tiff":
            with Image.open(
                BytesIO(file_bytes) if self.file_path.startswith("s3://") else self.file_path
            ) as img:
                return img.n_frames
        elif mime_type in ["image/jpeg", "image/png"]:
            return 1
        elif mime_type in [
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]:
            try:
                from docx import Document

                document = Document(
                    BytesIO(file_bytes) if self.file_path.startswith("s3://") else self.file_path
                )
                # Assuming paragraphs as a proxy for pages
                return len(document.paragraphs)
            except ImportError:
                logger.error("python-docx library is not installed")
                raise ImportError(
                    "The 'python-docx' library is not installed. Please install it to process .docx files.",
                    "pip install python-docx",
                )
        else:
            logger.error(f"Unsupported file type: {mime_type}")
            raise ValueError(f"Unsupported file type: {mime_type}")

    def get_current_window_pages(self) -> List[int]:
        """
        Get the page numbers in the current window.

        Returns:
            List[int]: List of page numbers in the current window.
        """
        end_page = min(self.current_window_start + self.window_size - 1, self.total_pages)
        return list(range(self.current_window_start, end_page + 1))

    def move_to_next_window(self, overlap: int = 2) -> bool:
        """
        Move to the next window of pages with optional overlap.

        Args:
            overlap (int, optional): Number of pages to overlap with the previous window. Defaults to 2.

        Returns:
            bool: True if successfully moved to the next window, False if already at the end.
        """
        if self.current_window_start + self.window_size > self.total_pages:
            return False  # Already at the end

        # Move the window forward, keeping some overlap with the previous window
        self.current_window_start = self.current_window_start + self.window_size - overlap

        # Make sure we don't go beyond the total pages
        if self.current_window_start > self.total_pages:
            self.current_window_start = self.total_pages - self.window_size + 1
            if self.current_window_start < 1:
                self.current_window_start = 1

        return True

    def move_to_previous_window(self, overlap: int = 2) -> bool:
        """
        Move to the previous window of pages with optional overlap.

        Args:
            overlap (int, optional): Number of pages to overlap with the next window. Defaults to 2.

        Returns:
            bool: True if successfully moved to the previous window, False if already at the beginning.
        """
        if self.current_window_start <= 1:
            return False  # Already at the beginning

        # Move the window backward, keeping some overlap with the next window
        self.current_window_start = self.current_window_start - self.window_size + overlap

        # Make sure we don't go below page 1
        if self.current_window_start < 1:
            self.current_window_start = 1

        return True

    def move_to_specific_window(self, start_page: int) -> bool:
        """
        Move to a specific window starting at the given page.

        Args:
            start_page (int): The starting page number for the window.

        Returns:
            bool: True if successfully moved to the specified window, False otherwise.
        """
        if start_page < 1 or start_page > self.total_pages:
            return False

        self.current_window_start = start_page
        return True

    def get_window_info(self) -> Dict[str, Any]:
        """
        Get information about the current window and document.

        Returns:
            Dict[str, Any]: Dictionary containing window information.
        """
        current_pages = self.get_current_window_pages()
        return {
            "total_pages": self.total_pages,
            "current_window_start": self.current_window_start,
            "current_window_end": current_pages[-1],
            "current_window_size": len(current_pages),
            "has_previous_window": self.current_window_start > 1,
            "has_next_window": current_pages[-1] < self.total_pages,
        }

    def get_pages_as_base64(self) -> List[Dict[str, Union[int, str]]]:
        """
        Get the current window of pages as base64 encoded strings.

        Returns:
            List[Dict[str, Union[int, str]]]: List of dictionaries containing page numbers and base64 encoded strings.
        """
        pages = self.get_current_window_pages()
        converter = FileConverter(file_path=self.file_path, pages=pages, s3_client=self.s3_client)
        return converter.convert_to_base64()

    def get_pages_as_bytes(self) -> List[Dict[str, Union[int, bytes]]]:
        """
        Get the current window of pages as bytes.

        Returns:
            List[Dict[str, Union[int, bytes]]]: List of dictionaries containing page numbers and bytes.
        """
        pages = self.get_current_window_pages()
        converter = FileConverter(file_path=self.file_path, pages=pages, s3_client=self.s3_client)
        return converter.convert_to_bytes()

    def process_document(
        self, processor_func, use_converse_api: bool = False, overlap: int = 2, **kwargs
    ) -> List[Any]:
        """
        Process the entire document using a sliding window approach.

        Args:
            processor_func: Function that processes a window of pages and returns a result.
            use_converse_api (bool, optional): Whether to use converse API or invoke_model API. Defaults to False.
            overlap (int, optional): Number of pages to overlap between windows. Defaults to 2.
            **kwargs: Additional arguments to pass to the processor function.

        Returns:
            List[Any]: List of results from processing each window.
        """
        results = []

        # Reset to the beginning
        self.current_window_start = 1

        while True:
            # Get current window pages
            pages = self.get_current_window_pages()

            # Process the current window
            if use_converse_api:
                page_data = self.get_pages_as_bytes()
            else:
                page_data = self.get_pages_as_base64()

            # Add window information to kwargs
            window_info = self.get_window_info()
            kwargs.update({"window_info": window_info})

            print(f"Processing pages: {pages}")
            # Process the current window
            result = processor_func(page_data, **kwargs)
            results.append(result)

            # Move to the next window
            if not self.move_to_next_window(overlap=overlap):
                break

        return results
