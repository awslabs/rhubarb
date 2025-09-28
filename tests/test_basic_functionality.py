# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from unittest.mock import Mock
import boto3
from rhubarb import DocAnalysis, VideoAnalysis, DocClassification, LanguageModels, EmbeddingModels


class TestBasicFunctionality:
    @pytest.fixture
    def mock_session(self):
        session = Mock(spec=boto3.Session)
        session.client.return_value = Mock()
        return session

    @pytest.fixture
    def test_pdf_file(self, tmp_path):
        """Create a temporary test PDF file."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")
        return str(test_file)

    def test_doc_analysis_initialization(self, mock_session, test_pdf_file):
        """Test DocAnalysis can be initialized."""
        da = DocAnalysis(file_path=test_pdf_file, boto3_session=mock_session)
        assert da.file_path == test_pdf_file
        assert da.modelId == LanguageModels.CLAUDE_SONNET_V2
        assert da.max_tokens == 1024
        assert da.temperature == 0

    def test_doc_analysis_custom_params(self, mock_session, test_pdf_file):
        """Test DocAnalysis with custom parameters."""
        da = DocAnalysis(
            file_path=test_pdf_file,
            boto3_session=mock_session,
            modelId=LanguageModels.CLAUDE_OPUS_V1,
            max_tokens=2048,
            temperature=0.5
        )
        assert da.modelId == LanguageModels.CLAUDE_OPUS_V1
        assert da.max_tokens == 2048
        assert da.temperature == 0.5

    def test_video_analysis_initialization(self, mock_session):
        """Test VideoAnalysis can be initialized."""
        va = VideoAnalysis(
            file_path="s3://bucket/video.mp4",
            boto3_session=mock_session
        )
        assert va.file_path == "s3://bucket/video.mp4"
        # VideoAnalysis defaults to NOVA_LITE for video processing
        assert va.modelId == LanguageModels.NOVA_LITE

    def test_doc_classification_initialization(self, mock_session, test_pdf_file):
        """Test DocClassification can be initialized."""
        dc = DocClassification(
            file_path=test_pdf_file,
            boto3_session=mock_session,
            classification_samples=["invoice", "receipt", "contract"]
        )
        # Test that it initializes with correct model
        assert dc.modelId == EmbeddingModels.TITAN_EMBED_MM_V1

    def test_s3_file_paths(self, mock_session):
        """Test S3 file path handling."""
        da = DocAnalysis(
            file_path="s3://bucket/file.pdf",
            boto3_session=mock_session
        )
        assert da.file_path == "s3://bucket/file.pdf"

    def test_model_enums(self):
        """Test that model enums are accessible."""
        assert LanguageModels.CLAUDE_SONNET_V2.value == "anthropic.claude-3-5-sonnet-20240620-v1:0"
        assert LanguageModels.NOVA_PRO.value == "amazon.nova-pro-v1:0"
        assert EmbeddingModels.TITAN_EMBED_MM_V1.value == "amazon.titan-embed-image-v1"

    def test_exception_imports(self):
        """Test that custom exceptions are importable."""
        from rhubarb import (
            RhubarbError, DocumentProcessingError, VideoProcessingError,
            ClassificationError, ModelInvocationError, FileFormatError,
            S3AccessError, ValidationError, ConfigurationError
        )
        
        # Test exception hierarchy
        assert issubclass(DocumentProcessingError, RhubarbError)
        assert issubclass(VideoProcessingError, RhubarbError)
        assert issubclass(ValidationError, RhubarbError)
