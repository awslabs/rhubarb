# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from enum import Enum


class LanguageModels(Enum):
    CLAUDE_OPUS_4_6 = "anthropic.claude-opus-4-6-v1"
    CLAUDE_SONNET_4_6 = "anthropic.claude-sonnet-4-6"
    CLAUDE_HAIKU_4_5 = "anthropic.claude-haiku-4-5-20251001-v1:0"
    NOVA_PRO = "amazon.nova-pro-v1:0"
    NOVA_LITE = "amazon.nova-lite-v1:0"
    NOVA_2_LITE = "amazon.nova-2-lite-v1:0"


class EmbeddingModels(Enum):
    TITAN_EMBED_MM_V1 = "amazon.titan-embed-image-v1"
