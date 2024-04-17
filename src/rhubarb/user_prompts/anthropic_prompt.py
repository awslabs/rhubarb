# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Any, List, Optional

import jsonschema

from rhubarb.file_converter import FileConverter
from rhubarb.system_prompts import SystemPrompts


class AnthropicMessages:
    def __init__(
        self,
        file_path: str,
        s3_client: Optional[Any],
        system_prompt: str,
        message: str,
        max_tokens: int,
        temperature: int,
        pages: List[int],
        output_schema: Optional[dict] = None,
        message_history: Optional[List[dict]] = None,
    ) -> None:
        self.file_path = file_path
        self.s3_client = s3_client
        self.system_prompt = system_prompt
        self.message = message
        self.output_schema = output_schema
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.pages = pages
        self.message_history = message_history

    def _get_base64_from_doc(self) -> List[dict]:
        fc = FileConverter(
            file_path=self.file_path, s3_client=self.s3_client, pages=self.pages
        )
        base64_pages = fc.convert_to_base64()
        return base64_pages

    def _validate_if_schema(self) -> str:
        if self.output_schema:

            try:
                meta_schema = jsonschema.Draft7Validator.META_SCHEMA
                jsonschema.validate(instance=self.output_schema, schema=meta_schema)
            except jsonschema.exceptions.ValidationError as e:
                raise e

            encouragement = "Take a deep breath and answer this question as accurately as possible.\n"
            self.system_prompt = SystemPrompts().SchemaSysPrompt
            if (
                "rephrased_question" in self.output_schema
                and "output_schema" in self.output_schema
            ):
                self.message = f"Given the following schema:\n<schema>{json.dumps(self.output_schema['output_schema'])}<schema>\n \
                                {encouragement}\n \
                                <question>{self.output_schema['rephrased_question']}</question>"
            else:
                self.message = f"Given the following schema:\n<schema>{json.dumps(self.output_schema)}<schema>\n \
                                {encouragement}\n \
                                <question>{self.message}</question>"

    def _construct_with_history(self) -> List[dict]:
        messages = self.message_history
        messages.append({"type": "text", "text": self.message})
        return messages

    def _construct_base64_messages(self, base64_pages: List[Any]) -> List[dict]:        
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

    def messages(self) -> str:
        body = {}
        if not self.message_history:
            self._validate_if_schema()
            base64_pages = self._get_base64_from_doc()
            messages = self._construct_base64_messages(base64_pages=base64_pages)
            body["messages"] = messages
        else:
            messages = self._construct_with_history()
            body["messages"] = messages

        body["system"] = self.system_prompt
        body["anthropic_version"] = "bedrock-2023-05-31"
        body["max_tokens"] = self.max_tokens
        body["temperature"] = self.temperature
        return body
