# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, List, Optional, Generator

from pydantic import Field, BaseModel, PrivateAttr, model_validator
from botocore.config import Config

from rhubarb.models import LanguageModels
from rhubarb.invocations import Invocations
from rhubarb.user_prompts import AnthropicMessages
from rhubarb.system_prompts import SystemPrompts

logger = logging.getLogger(__name__)


class DocAnalysis(BaseModel):
    """
    Analyzes a document using the specified Bedrock Language Model.

    Args:
    - `file_path` (str): File path of the document, local or S3 path.
    - `modelId` (LanguageModels, optional): Bedrock Model ID. Defaults to LanguageModels.CLAUDE_SONNET_V1.
    - `system_prompt` (str, optional): System prompt. Defaults to SystemPrompts().DefaultSysPrompt.
    - `boto3_session` (Any): Instance of boto3.session.Session.
    - `max_tokens` (int, optional): The maximum number of tokens to generate before stopping. Max 4096 tokens for Claude models. Defaults to 1024.
    - `temperature` (int, optional): Amount of randomness injected into the response. Ranges from 0.0 to 1.0. Defaults to 0.
    - `pages` (List[int], optional): Pages of a multi-page PDF or TIF to process. [0] will process all pages upto 20 pages max,
    [1,3,5] will process pages 1, 3 and 5. Defaults to [0].

    Attributes:
    - `bedrock_client` (Optional[Any]): boto3 bedrock-runtime client, will get overriten by boto3_session.
    - `s3_client` (Optional[Any]): boto3 s3 client, will get overriten by boto3_session.

    Usage:
        ```python
        da = DocAnalysis(
            file_path="s3://my-bucket/my-document.pdf",
            boto3_session=boto3.Session(),
            max_tokens=2048,
            temperature=0,
            pages=[1, 3, 5]
        )
        ```
    """

    file_path: str
    """File path of the document, local or S3 path"""

    modelId: LanguageModels = Field(default=LanguageModels.CLAUDE_SONNET_V1)
    """Bedrock Model ID"""

    system_prompt: str = Field(default=SystemPrompts().DefaultSysPrompt)
    """System prompt"""

    boto3_session: Any
    """Instance of boto3.session.Session"""

    max_tokens: int = Field(default=1024)
    """The maximum number of tokens to generate before stopping.
    Max 4096 tokens for Claude models
    """

    temperature: float = Field(default=0.0)
    """Amount of randomness injected into the response.
    Ranges from 0.0 to 1.0
    """

    pages: List[int] = Field(default=[0])
    """Pages of a multi-page PDF or TIF to process
    - [0] will process all pages upto 20 pages max
    - [1,3,5] will process pages 1, 3 and 5
    """

    _message_history: List[Any] = PrivateAttr(default=None)
    """History of user/assistant messages"""

    _bedrock_client: Any = PrivateAttr(default=None)
    """boto3 bedrock-runtime client, will get overriten by boto3_session"""

    _s3_client: Any = PrivateAttr(default=None)
    """boto3 s3 client, will get overriten by boto3_session"""

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, values: dict) -> dict:
        file_path = values.get("file_path")
        pages = values.get("pages", [0])

        if 0 in pages and len(pages) > 1:
            logger.error("If specific pages are provided, page number 0 is invalid.")
            raise ValueError("If specific pages are provided, page number 0 is invalid.")

        if len(pages) > 20:
            logger.error("Cannot process more than 20 pages at a time.")
            raise ValueError("Cannot process more than 20 pages at a time.")

        blocked_schemes = ["http://", "https://", "ftp://"]
        if any(file_path.startswith(scheme) for scheme in blocked_schemes):
            logger.error("file_path must be a local file system path or an s3:// path")
            raise ValueError("file_path must be a local file system path or an s3:// path")

        s3_config = Config(
            retries={"max_attempts": 0, "mode": "standard"}, signature_version="s3v4"
        )
        br_config = Config(retries={"max_attempts": 0, "mode": "standard"})
        session = values.get("boto3_session")
        cls._s3_client = session.client("s3", config=s3_config)
        cls._bedrock_client = session.client("bedrock-runtime", config=br_config)

        return values

    @property
    def history(self) -> Any:
        return self._message_history

    def _get_anthropic_prompt(
        self,
        message: Any,
        sys_prompt: str,
        output_schema: Optional[dict] = None,
        history: Optional[List[dict]] = None,
    ) -> Any:
        return AnthropicMessages(
            file_path=self.file_path,
            s3_client=self._s3_client,
            system_prompt=sys_prompt,
            message=message,
            output_schema=output_schema,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            pages=self.pages,
            message_history=history,
        )

    def run(
        self,
        message: str,
        output_schema: Optional[dict] = None,
        history: Optional[List[dict]] = None,
    ) -> Any:
        """
        Invokes the specified language model with the given message and optional output schema.

        Args:
        - `message` (`str`): The input message or prompt for the language model.
        - `output_schema` (`Optional[dict]`, optional): The output JSON schema for the language model response. Defaults to None.
        """
        if (
            self.modelId == LanguageModels.CLAUDE_HAIKU_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V2
        ):
            a_msg = self._get_anthropic_prompt(
                message=message,
                output_schema=output_schema,
                sys_prompt=self.system_prompt,
                history=history,
            )
            body = a_msg.messages()

        model_invoke = Invocations(
            body=body,
            bedrock_client=self._bedrock_client,
            model_id=self.modelId.value,
            output_schema=output_schema,
        )
        response = model_invoke.invoke_model_json()
        self._message_history = model_invoke.message_history
        return response

    def run_stream(
        self, message: Any, history: Optional[List[dict]] = None
    ) -> Generator[Any, Any, Any]:
        """
        Invokes the specified language model with the given message in streaming mode.

        Args:
        - `message` (`Any`): The input message or prompt for the language model.
        """
        if (
            self.modelId == LanguageModels.CLAUDE_HAIKU_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V2
        ):
            a_msg = self._get_anthropic_prompt(
                message=message, sys_prompt=self.system_prompt, history=history
            )
            body = a_msg.messages()

        model_invoke = Invocations(
            body=body, bedrock_client=self._bedrock_client, model_id=self.modelId.value
        )
        for response in model_invoke.invoke_model_stream():
            yield response
        self._message_history = model_invoke.message_history

    def run_entity(self, message: Any, entities: List[Any]) -> Any:
        """
        Invokes the specified language model with the given message in streaming mode.

        Args:
        - `message` (`Any`): The input message or prompt for the language model.
        - `entities` (`List[Entities.entity]`): A list of entities to be detected
        """
        if (
            self.modelId == LanguageModels.CLAUDE_HAIKU_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V2
        ):
            sys_prompt = SystemPrompts(entities=entities).NERSysPrompt
            a_msg = self._get_anthropic_prompt(message=message, sys_prompt=sys_prompt)
            body = a_msg.messages()

        model_invoke = Invocations(
            body=body, bedrock_client=self._bedrock_client, model_id=self.modelId.value
        )
        response = model_invoke.invoke_model_json()
        return response

    def generate_schema(self, message: str, assistive_rephrase: Optional[bool] = False) -> dict:
        """
        Invokes the specified language model with the given message to genereate a JSON
        schema for a given document.

        Args:
        - `message` (`Any`): The input message or prompt for the language model.
        - `assistive_rephrase` (`bool`): If set to true, will rephrase the question properly for subsequent use
        """
        if (
            self.modelId == LanguageModels.CLAUDE_HAIKU_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V2
        ):
            if assistive_rephrase:
                sys_prompt = SystemPrompts().SchemaGenSysPromptWithRephrase
            else:
                sys_prompt = SystemPrompts().SchemaGenSysPrompt
            a_msg = self._get_anthropic_prompt(message=message, sys_prompt=sys_prompt)
            body = a_msg.messages()

        model_invoke = Invocations(
            body=body, bedrock_client=self._bedrock_client, model_id=self.modelId.value
        )
        response = model_invoke.invoke_model_json()
        return response
