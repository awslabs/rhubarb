# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from unittest.mock import Mock, patch
import boto3
from rhubarb import DocClassification, EmbeddingModels


class TestDocClassification:
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
    def doc_classification(self, mock_session, test_pdf_file):
        return DocClassification(
            file_path=test_pdf_file,
            boto3_session=mock_session,
            classification_samples=["invoice", "receipt", "contract"]
        )

    def test_init_with_samples(self, mock_session, test_pdf_file):
        samples = ["invoice", "receipt", "contract"]
        dc = DocClassification(
            file_path=test_pdf_file,
            boto3_session=mock_session,
            classification_samples=samples
        )
        assert dc.classification_samples == samples

    def test_default_embedding_model(self, mock_session, test_pdf_file):
        dc = DocClassification(
            file_path=test_pdf_file,
            boto3_session=mock_session,
            classification_samples=["test"]
        )
        assert dc.embedding_model == EmbeddingModels.TITAN_EMBED_MM_V1

    @patch('rhubarb.classification.classification.Invocations')
    def test_classify_success(self, mock_invocations, doc_classification):
        mock_inv = Mock()
        mock_inv.invoke_embedding.return_value = {
            "classification": "invoice",
            "confidence": 0.95
        }
        mock_invocations.return_value = mock_inv
        
        result = doc_classification.classify()
        
        assert "classification" in result
        assert "confidence" in result

    def test_bedrock_client_initialization(self, mock_session, test_pdf_file):
        """Test that clients are initialized correctly."""
        dc = DocClassification(
            file_path=test_pdf_file,
            boto3_session=mock_session,
            classification_samples=["test"]
        )
        
        assert dc.bedrock_client is not None
        assert dc.s3_client is not None

    def test_s3_file_path(self, mock_session):
        """Test S3 file path handling."""
        dc = DocClassification(
            file_path="s3://bucket/file.pdf",
            boto3_session=mock_session,
            classification_samples=["test"]
        )
        assert dc.file_path == "s3://bucket/file.pdf"
