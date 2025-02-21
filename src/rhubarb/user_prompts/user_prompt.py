# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Any, List, Optional

import jsonschema

from rhubarb.file_converter import FileConverter
from rhubarb.system_prompts import SystemPrompts


class UserMessages:
    def __init__(
        self,
        file_path: str,
        s3_client: Optional[Any],
        system_prompt: str,
        message: str,
        max_tokens: int,
        temperature: int,
        pages: List[int],
        use_converse_api: bool,
        output_schema: Optional[dict] = None,
        message_history: Optional[List[dict]] = None,
        modelId: Optional[Any] = None,
    ) -> None:
        self.file_path = file_path
        self.s3_client = s3_client
        self.system_prompt = system_prompt
        self.message = message
        self.output_schema = output_schema
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.pages = pages
        self.use_converse_api = use_converse_api
        self.message_history = message_history
        self.modelId = modelId

    def _get_pages_from_doc(self) -> List[dict]:
        fc = FileConverter(file_path=self.file_path, s3_client=self.s3_client, pages=self.pages)
        if self.use_converse_api:
            byte_pages = fc.convert_to_bytes()
            return byte_pages
        else:
            base64_pages = fc.convert_to_base64()
            return base64_pages

    def _validate_if_schema(self) -> str:
        if self.output_schema:
            try:
                meta_schema = jsonschema.Draft7Validator.META_SCHEMA
                jsonschema.validate(instance=self.output_schema, schema=meta_schema)
            except jsonschema.exceptions.ValidationError as e:
                raise e

            encouragement = (
                "Take a deep breath and answer this question as accurately as possible.\n"
            )
            self.system_prompt = SystemPrompts().SchemaSysPrompt
            if "rephrased_question" in self.output_schema and "output_schema" in self.output_schema:
                self.message = f"Given the following schema:\n<schema>{json.dumps(self.output_schema['output_schema'])}<schema>\n \
                                {encouragement}\n \
                                <question>{self.output_schema['rephrased_question']}</question>"
            else:
                self.message = f"Given the following schema:\n<schema>{json.dumps(self.output_schema)}<schema>\n \
                                {encouragement}\n \
                                <question>{self.message}</question>"

    def _construct_messages_with_history(self) -> List[dict]:
        messages = self.message_history
        if self.use_converse_api:
            messages.append({"text": self.message})
        else:
            messages.append({"type": "text", "text": self.message})
        return messages

    def _construct_invoke_messages(self, base64_pages: List[Any]) -> List[dict]:
        if str(self.modelId).__contains__("NOVA"):
            # Nova format
            content = []

            # Add the initial text prompt if message exists
            if self.message:
                content.append({"text": self.message})

            # Add images from pages
            for page in base64_pages:
                content.append(
                    {"image": {"format": "png", "source": {"bytes": page["base64string"]}}}
                )

            # Construct the final message structure
            user_message = [{"role": "user", "content": content}]
        else:
            # Claude format
            content = [
                item
                for page in base64_pages
                for item in [
                    {"type": "text", "text": f"Page: {page['page']}"},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": page["base64string"],
                        },
                    },
                ]
            ]
            content.append({"type": "text", "text": self.message})
            user_message = [{"role": "user", "content": content}]
        return user_message

    def _construct_converse_messages(self, byte_pages: List[Any]) -> List[dict]:
        content = [
            item
            for page in byte_pages
            for item in [
                {"text": f"Page: {page['page']}"},
                {"image": {"format": "png", "source": {"bytes": page["image_bytes"]}}},
            ]
        ]
        content.append({"text": self.message})
        user_message = [{"role": "user", "content": content}]
        return user_message

    def messages(self) -> str:
        """
        Function messages creates messages payload for either `invoke_model` API
        or `converse` API depending on which API is being used.
        """
        body = {}
        messages = []
        if not self.message_history:
            self._validate_if_schema()
            doc_pages = self._get_pages_from_doc()
            if self.use_converse_api:
                messages = self._construct_converse_messages(byte_pages=doc_pages)
            else:
                messages = self._construct_invoke_messages(base64_pages=doc_pages)
            body["messages"] = messages
        else:
            messages = self._construct_messages_with_history()
            body["messages"] = messages

        if self.use_converse_api:
            body["system"] = [{"text": self.system_prompt}]
            body["inferenceConfig"] = {
                "maxTokens": self.max_tokens,
                "temperature": self.temperature,
            }
        else:
            # Check if it's a Nova model
            if str(self.modelId).__contains__("NOVA"):
                body["system"] = [{"text": self.system_prompt}]
            else:
                # Claude models
                body["system"] = self.system_prompt
                body["max_tokens"] = self.max_tokens
                body["temperature"] = self.temperature
                body["anthropic_version"] = "bedrock-2023-05-31"

        return body
