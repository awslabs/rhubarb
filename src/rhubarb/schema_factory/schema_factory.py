# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import json
import logging

logger = logging.getLogger(__name__)


class SchemaFactory:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    def __getattr__(self, name):
        # Construct the filename assuming the property name matches the JSON file name
        json_filename = f"{name.lower()}.json"
        filepath = os.path.join(self.BASE_DIR, "single_doc_schemas", json_filename)

        if not os.path.exists(filepath):
            logger.error(f"No such JSON file: {json_filename} in {filepath}")
            raise AttributeError(f"No such JSON file: {json_filename} in {filepath}")

        # Load and return the JSON file content directly
        with open(filepath, "r") as json_file:
            return json.load(json_file)
