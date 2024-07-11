# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from enum import Enum


class LanguageModels(Enum):
    CLAUDE_OPUS_V1 = "anthropic.claude-3-opus-20240229-v1:0"
    CLAUDE_SONNET_V1 = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_HAIKU_V1 = "anthropic.claude-3-haiku-20240307-v1:0"
    CLAUDE_SONNET_V2 = "anthropic.claude-3-5-sonnet-20240620-v1:0"


class EmbeddingModels(Enum):
    TITAN_EMBED_MM_V1 = "amazon.titan-embed-image-v1"
