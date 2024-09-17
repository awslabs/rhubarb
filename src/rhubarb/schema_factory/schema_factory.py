# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import json
import logging

from .default_models import (
    NERModel,
    ChatModel,
    FigureModel,
    DefaultModel,
    MultiClassModel,
    ClassificationModel,
)

logger = logging.getLogger(__name__)


class SchemaFactory:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    def __getattr__(self, name):
        if name.lower() == "chat_schema":
            return ChatModel.model_json_schema()
        if name.lower() == "default_schema":
            return DefaultModel.model_json_schema()
        if name.lower() == "classification_schema":
            return ClassificationModel.model_json_schema()
        if name.lower() == "multiclass_schema":
            return MultiClassModel.model_json_schema()
        if name.lower() == "ner_schema":
            return NERModel.model_json_schema()
        if name.lower() == "figure_schema":
            return FigureModel.model_json_schema()
        if name.lower() == "sample_schema":
            json_filename = f"{name.lower()}.json"
            filepath = os.path.join(self.BASE_DIR, "fewshot", json_filename)
            if not os.path.exists(filepath):
                logger.error(f"No such JSON file: {json_filename} in {filepath}")
                raise AttributeError(f"No such JSON file: {json_filename} in {filepath}")

            with open(filepath, "r") as json_file:
                return json.load(json_file)

    # def __getattr__(self, name):
    #     json_filename = f"{name.lower()}.json"
    #     filepath = os.path.join(self.BASE_DIR, "single_doc_schemas", json_filename)

    #     if not os.path.exists(filepath):
    #         logger.error(f"No such JSON file: {json_filename} in {filepath}")
    #         raise AttributeError(f"No such JSON file: {json_filename} in {filepath}")

    #     with open(filepath, "r") as json_file:
    #         return json.load(json_file)
