# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from unittest.mock import Mock, patch
import boto3
from rhubarb import VideoAnalysis, LanguageModels


class TestVideoAnalysis:
    @pytest.fixture
    def mock_session(self):
        session = Mock(spec=boto3.Session)
        session.client.return_value = Mock()
        return session

    @pytest.fixture
    def video_analysis(self, mock_session):
        return VideoAnalysis(
            file_path="s3://bucket/video.mp4",
            boto3_session=mock_session
        )

    def test_init_with_s3_path(self, mock_session):
        va = VideoAnalysis(
            file_path="s3://bucket/video.mp4",
            boto3_session=mock_session
        )
        assert va.file_path == "s3://bucket/video.mp4"

    def test_supported_video_formats(self, mock_session):
        formats = [".mp4", ".avi", ".mov", ".mkv"]
        for fmt in formats:
            va = VideoAnalysis(
                file_path=f"s3://bucket/video{fmt}",
                boto3_session=mock_session
            )
            assert va.file_path.endswith(fmt)

    @patch('rhubarb.video_processor.video_analyzer.Invocations')
    def test_run_success(self, mock_invocations, video_analysis):
        mock_inv = Mock()
        mock_inv.invoke_model.return_value = "Video analysis result"
        mock_invocations.return_value = mock_inv
        
        result = video_analysis.run(message="What happens in this video?")
        
        assert result == "Video analysis result"

    def test_bedrock_client_initialization(self, mock_session):
        """Test that clients are initialized correctly."""
        va = VideoAnalysis(
            file_path="s3://bucket/video.mp4",
            boto3_session=mock_session
        )
        
        assert va.bedrock_client is not None
        assert va.s3_client is not None

    def test_default_model(self, mock_session):
        """Test default model selection."""
        va = VideoAnalysis(
            file_path="s3://bucket/video.mp4",
            boto3_session=mock_session
        )
        
        assert va.modelId == LanguageModels.CLAUDE_SONNET_V2

    def test_custom_model(self, mock_session):
        """Test custom model selection."""
        va = VideoAnalysis(
            file_path="s3://bucket/video.mp4",
            boto3_session=mock_session,
            modelId=LanguageModels.NOVA_PRO
        )
        
        assert va.modelId == LanguageModels.NOVA_PRO
