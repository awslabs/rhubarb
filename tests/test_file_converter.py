import os
import unittest
from unittest.mock import MagicMock, patch

from rhubarb.file_converter import FileConverter


class TestFileConverter(unittest.TestCase):
    def setUp(self):
        self.png_file_path = os.path.join(os.path.dirname(__file__), "test_docs", "cameras.png")
        self.jpg_file_path = os.path.join(os.path.dirname(__file__), "test_docs", "birth_cert.jpeg")
        self.pdf_file_path = os.path.join(os.path.dirname(__file__), "test_docs", "bank_stmt.pdf")
        self.multi_pdf_file_path = os.path.join(
            os.path.dirname(__file__), "test_docs", "employee_enrollment.pdf"
        )
        self.tiff_file_path = os.path.join(os.path.dirname(__file__), "test_docs", "memorandum.tif")

    @patch("boto3.client")
    def test_s3_file_conversion(self, mock_boto3_client):
        mock_boto3_client = MagicMock()
        with open(self.png_file_path, "rb") as f:
            file_bytes = f.read()

        # Mock S3 response to return file bytes
        mock_streaming_body = MagicMock()
        mock_streaming_body.read.return_value = file_bytes
        mock_s3_response = {"Body": mock_streaming_body}
        mock_boto3_client.get_object.return_value = mock_s3_response

        # Mock S3 path
        s3_png_file_path = "s3://bucket/test.png"
        converter = FileConverter(s3_png_file_path, pages=[0], s3_client=mock_boto3_client)
        result = converter.convert_to_base64()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("base64string", result[0])

    @patch("boto3.client")
    def test_local_png_file_conversion(self, mock_boto3_client):
        mock_boto3_client = MagicMock()
        converter = FileConverter(
            file_path=self.png_file_path, pages=[0], s3_client=mock_boto3_client
        )
        result = converter.convert_to_base64()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("base64string", result[0])

    @patch("boto3.client")
    def test_local_jpg_file_conversion(self, mock_boto3_client):
        mock_boto3_client = MagicMock()
        converter = FileConverter(
            file_path=self.jpg_file_path, pages=[0], s3_client=mock_boto3_client
        )
        result = converter.convert_to_base64()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("base64string", result[0])

    @patch("boto3.client")
    def test_local_pdf_file_conversion(self, mock_boto3_client):
        mock_boto3_client = MagicMock()
        converter = FileConverter(
            file_path=self.pdf_file_path, pages=[0], s3_client=mock_boto3_client
        )
        result = converter.convert_to_base64()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for page in result:
            self.assertIn("page", page)
            self.assertIn("base64string", page)

    @patch("boto3.client")
    def test_local_multipdf_file_conversion(self, mock_boto3_client):
        mock_boto3_client = MagicMock()
        converter = FileConverter(
            file_path=self.multi_pdf_file_path, pages=[0], s3_client=mock_boto3_client
        )
        result = converter.convert_to_base64()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        for page in result:
            self.assertIn("page", page)
            self.assertIn("base64string", page)

    @patch("boto3.client")
    def test_local_tiff_file_conversion(self, mock_boto3_client):
        mock_boto3_client = MagicMock()
        converter = FileConverter(
            file_path=self.tiff_file_path, pages=[0], s3_client=mock_boto3_client
        )
        result = converter.convert_to_base64()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for page in result:
            self.assertIn("page", page)
            self.assertIn("base64string", page)


if __name__ == "__main__":
    unittest.main()
