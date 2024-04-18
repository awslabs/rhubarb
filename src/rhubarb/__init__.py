# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
import importlib.metadata
from logging import NullHandler

from .models import LanguageModels, EmbeddingModels
from .analyze import DocAnalysis
from .classify import DocClassification
from .config.config import GlobalConfig
from .schema_factory.entities import Entities
from .system_prompts.system_prompts import SystemPrompts

logging.getLogger(__name__).addHandler(NullHandler())

__version__ = importlib.metadata.version("pyrhubarb")

__all__ = [
    "DocAnalysis",
    "DocClassification",
    "LanguageModels",
    "EmbeddingModels",
    "SystemPrompts",
    "Entities",
    "GlobalConfig",
]
