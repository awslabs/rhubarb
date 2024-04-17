import os
import json
import unittest
from unittest.mock import MagicMock, patch

from rhubarb import DocAnalysis


class TestExtractions(unittest.TestCase):
    def setUp(self):
        self.multi_pdf_file_path = os.path.join(
            os.path.dirname(__file__), "test_docs", "employee_enrollment.pdf"
        )

        # Patch the boto3.Session constructor to return a mock session object
        self.mock_session_patcher = patch("boto3.Session")
        self.mock_session = self.mock_session_patcher.start()
        self.addCleanup(self.mock_session_patcher.stop)

        # Create mock clients for S3 and Bedrock
        self.mock_s3_client = MagicMock()
        self.mock_bedrock_client = MagicMock()

        # Configure the mock session to return the appropriate mock client
        def client_side_effect(service_name, *args, **kwargs):
            if service_name == "s3":
                return self.mock_s3_client
            elif service_name == "bedrock-runtime":
                return self.mock_bedrock_client
            else:
                raise ValueError("Unsupported service")

        self.mock_session.return_value.client.side_effect = client_side_effect

    def test_basic_qa(self):
        model_response = [
            {"page": 1, "detected_languages": ["English"], "content": "Cali Flores"},
            {"page": 3, "detected_languages": ["English"], "content": "Loki Flores"},
        ]
        api_response = {
            "role": "assistant",
            "content": [{"type": "text", "text": f"```json\n{json.dumps(model_response)}\n```"}],
            "usage": {"input_tokens": 5063, "output_tokens": 95},
        }
        mock_response_streaming = MagicMock()
        mock_streaming_body_content = json.dumps(api_response).encode(
            "utf-8"
        )  # Example JSON content
        mock_response_streaming.read.return_value = mock_streaming_body_content
        mock_response_streaming.__enter__.return_value = mock_response_streaming
        mock_response_streaming.__exit__.return_value = None

        mock_response = {"body": mock_response_streaming}
        self.mock_bedrock_client.invoke_model.return_value = mock_response

        da = DocAnalysis(file_path=self.multi_pdf_file_path, boto3_session=self.mock_session())
        response = da.run(message="What is the employee's name?")
        self.assertEqual(response["output"], model_response)
        self.assertEqual(response["token_usage"], {"input_tokens": 5063, "output_tokens": 95})
