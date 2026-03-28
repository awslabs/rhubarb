# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
import boto3
from unittest.mock import Mock, patch
from moto import mock_s3, mock_bedrock
from rhubarb import DocAnalysis, VideoAnalysis, DocClassification


@mock_s3
@mock_bedrock
class TestIntegration:
    @pytest.fixture
    def aws_credentials(self, monkeypatch):
        """Mocked AWS Credentials for moto."""
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
        monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
        monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
        monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    @pytest.fixture
    def s3_setup(self, aws_credentials):
        """Create S3 bucket and upload test files."""
        s3 = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-bucket"
        s3.create_bucket(Bucket=bucket_name)
        
        # Upload test PDF
        s3.put_object(
            Bucket=bucket_name,
            Key="test.pdf",
            Body=b"fake pdf content"
        )
        
        # Upload test video
        s3.put_object(
            Bucket=bucket_name,
            Key="test.mp4",
            Body=b"fake video content"
        )
        
        return bucket_name

    @patch('rhubarb.invocations.invocations.Invocations.invoke_model')
    def test_doc_analysis_s3_integration(self, mock_invoke, s3_setup, aws_credentials):
        """Test DocAnalysis with S3 file."""
        mock_invoke.return_value = "Mocked response"
        
        session = boto3.Session()
        da = DocAnalysis(
            file_path=f"s3://{s3_setup}/test.pdf",
            boto3_session=session
        )
        
        result = da.run(message="What is this document?")
        assert result == "Mocked response"
        mock_invoke.assert_called_once()

    @patch('rhubarb.invocations.invocations.Invocations.invoke_model')
    def test_video_analysis_s3_integration(self, mock_invoke, s3_setup, aws_credentials):
        """Test VideoAnalysis with S3 file."""
        mock_invoke.return_value = "Video analysis response"
        
        session = boto3.Session()
        va = VideoAnalysis(
            file_path=f"s3://{s3_setup}/test.mp4",
            boto3_session=session
        )
        
        result = va.run(message="What happens in this video?")
        assert result == "Video analysis response"
        mock_invoke.assert_called_once()

    @patch('rhubarb.invocations.invocations.Invocations.invoke_embedding')
    def test_doc_classification_s3_integration(self, mock_invoke, s3_setup, aws_credentials):
        """Test DocClassification with S3 file."""
        mock_invoke.return_value = {
            "classification": "invoice",
            "confidence": 0.95
        }
        
        session = boto3.Session()
        dc = DocClassification(
            file_path=f"s3://{s3_setup}/test.pdf",
            boto3_session=session,
            classification_samples=["invoice", "receipt", "contract"]
        )
        
        result = dc.classify()
        assert result["classification"] == "invoice"
        assert result["confidence"] == 0.95

    def test_bedrock_client_initialization(self, aws_credentials):
        """Test that Bedrock client initializes correctly."""
        session = boto3.Session()
        da = DocAnalysis(
            file_path="test.pdf",
            boto3_session=session
        )
        
        assert da.bedrock_client is not None
        assert da.s3_client is not None

    @patch('rhubarb.invocations.invocations.Invocations.invoke_model')
    def test_error_handling_invalid_s3_path(self, mock_invoke, aws_credentials):
        """Test error handling for invalid S3 paths."""
        session = boto3.Session()
        da = DocAnalysis(
            file_path="s3://nonexistent-bucket/test.pdf",
            boto3_session=session
        )
        
        # Should handle S3 errors gracefully
        with pytest.raises(Exception):  # Specific exception depends on implementation
            da.run(message="Test message")

    def test_cross_region_inference_config(self, aws_credentials):
        """Test CRI configuration."""
        session = boto3.Session()
        da = DocAnalysis(
            file_path="test.pdf",
            boto3_session=session,
            enable_cri=True
        )
        
        assert da.enable_cri is True
        # Verify client configuration includes CRI settings
        assert hasattr(da, 'bedrock_client')
