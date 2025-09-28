# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from unittest.mock import Mock, patch, MagicMock
import boto3
from rhubarb import DocAnalysis, LanguageModels


class TestDocAnalysis:
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

    @pytest.fixture
    def doc_analysis(self, mock_session, test_pdf_file):
        return DocAnalysis(
            file_path=test_pdf_file,
            boto3_session=mock_session
        )

    def test_init_with_defaults(self, mock_session, test_pdf_file):
        da = DocAnalysis(file_path=test_pdf_file, boto3_session=mock_session)
        assert da.file_path == test_pdf_file
        assert da.modelId == LanguageModels.CLAUDE_SONNET_V2
        assert da.max_tokens == 1024
        assert da.temperature == 0

    def test_init_with_custom_params(self, mock_session, test_pdf_file):
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

    def test_s3_file_path(self, mock_session):
        da = DocAnalysis(
            file_path="s3://bucket/file.pdf",
            boto3_session=mock_session
        )
        assert da.file_path == "s3://bucket/file.pdf"

    @patch('rhubarb.user_prompts.user_prompt.FileConverter')
    @patch('rhubarb.invocations.invocations.Invocations')
    def test_run_success(self, mock_invocations, mock_file_converter, doc_analysis):
        # Mock file converter
        mock_fc = Mock()
        mock_fc.get_images.return_value = [b"fake image data"]
        mock_file_converter.return_value = mock_fc
        
        # Mock invocations
        mock_inv = Mock()
        mock_inv.invoke_model.return_value = "Test response"
        mock_invocations.return_value = mock_inv
        
        result = doc_analysis.run(message="What is this document about?")
        
        assert result == "Test response"
        mock_inv.invoke_model.assert_called_once()

    def test_bedrock_client_initialization(self, mock_session, test_pdf_file):
        """Test that clients are initialized correctly."""
        da = DocAnalysis(
            file_path=test_pdf_file,
            boto3_session=mock_session
        )
        
        assert da.bedrock_client is not None
        assert da.s3_client is not None

    def test_enable_cri_flag(self, mock_session, test_pdf_file):
        """Test CRI configuration."""
        da = DocAnalysis(
            file_path=test_pdf_file,
            boto3_session=mock_session,
            enable_cri=True
        )
        
        assert da.enable_cri is True

    def test_converse_api_flag(self, mock_session, test_pdf_file):
        """Test converse API configuration."""
        da = DocAnalysis(
            file_path=test_pdf_file,
            boto3_session=mock_session,
            use_converse_api=True
        )
        
        assert da.use_converse_api is True

    def test_pages_parameter(self, mock_session, test_pdf_file):
        """Test pages parameter."""
        da = DocAnalysis(
            file_path=test_pdf_file,
            boto3_session=mock_session,
            pages=[1, 3, 5]
        )
        
        assert da.pages == [1, 3, 5]
