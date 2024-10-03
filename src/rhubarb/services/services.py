# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any

from botocore.config import Config

logger = logging.getLogger(__name__)


class BedrockService:
    def __init__(self, session: Any, model_id: str):
        self.session = session
        self.model_id = model_id
        self.bedrock = self._initialize_bedrock_client()

    def _initialize_bedrock_client(self) -> Any:
        br_config = Config(retries={"max_attempts": 0, "mode": "standard"})
        return self.session.client("bedrock", config=br_config)

    def get_inference_profile(self) -> str:
        """
        Search for a Bedrock model name in the inference profile list and return the corresponding inferenceProfileId.

        Returns:
        str: The inferenceProfileId if found, otherwise returns the on-demand model ID.
        """
        try:
            logger.info(
                f"Cross-region inference enabled. Checking inference profile for model_id {self.model_id}"
            )
            next_token = None
            while True:
                if next_token:
                    response = self.bedrock.list_inference_profiles(
                        maxResults=100, nextToken=next_token
                    )
                else:
                    response = self.bedrock.list_inference_profiles(maxResults=100)

                for profile in response["inferenceProfileSummaries"]:
                    for model in profile["models"]:
                        if self.model_id in model["modelArn"]:
                            logger.info(
                                f"Model inference profile Id {self.model_id} found for {self.model_id}."
                            )
                            return profile["inferenceProfileId"]

                next_token = response.get("nextToken")
                if not next_token:
                    break

            logger.info(f"No matching inference profile found for model_id {self.model_id}")
            return self.model_id

        except Exception as e:
            logger.error(
                f"An unexpected error occurred: {str(e)}, falling back to using model_id = {self.model_id}"
            )
            return self.model_id
