# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import mimetypes
from typing import Any, Dict, List, Tuple, Optional, Generator

from pydantic import Field, BaseModel, PrivateAttr, model_validator
from botocore.config import Config

from rhubarb.models import LanguageModels
from rhubarb.invocations import Invocations
from rhubarb.system_prompts import SystemPrompts

logger = logging.getLogger(__name__)


class VideoAnalysis(BaseModel):
    """
    Analyzes a video using the specified Bedrock Language Model.

    Args:
    - `file_path` (str): File path of the video, local or S3 path.
    - `modelId` (LanguageModels, optional): Bedrock Model ID. Defaults to LanguageModels.CLAUDE_SONNET_V2.
    - `system_prompt` (str, optional): System prompt. Defaults to SystemPrompts().VideoAnalysisSysPrompt.
    - `boto3_session` (Any): Instance of boto3.session.Session.
    - `max_tokens` (int, optional): The maximum number of tokens to generate before stopping. Max 4096 tokens for Claude models. Defaults to 1024.
    - `temperature` (int, optional): Amount of randomness injected into the response. Ranges from 0.0 to 1.0. Defaults to 0.
    - `frame_interval` (float, optional): Interval between frames in seconds. Defaults to 1.0.
    - `max_frames` (int, optional): Maximum number of frames to extract. Defaults to 20.
    - `use_converse_api` (bool, optional): Use Bedrock `converse` API to enable tool use. Defaults to `False` and uses `invoke_model`.
    - `enable_cri` (bool, optional): Enables Cross-region inference for certain models. Defaults to `False`.
    - `s3_bucket_owner` (str, optional): AWS account ID of the S3 bucket owner. Required for cross-account S3 access with Nova models.

    Attributes:
    - `bedrock_client` (Optional[Any]): boto3 bedrock-runtime client, will get overriten by boto3_session.
    - `s3_client` (Optional[Any]): boto3 s3 client, will get overriten by boto3_session.

    Usage:
        ```python
        va = VideoAnalysis(
            file_path="s3://my-bucket/my-video.mp4",
            boto3_session=boto3.Session(),
            max_tokens=2048,
            temperature=0,
            frame_interval=0.5,
            max_frames=30
        )
        ```
    """

    file_path: str
    """File path of the video, local or S3 path"""

    modelId: LanguageModels = Field(default=LanguageModels.NOVA_LITE)
    """Bedrock Model ID"""

    system_prompt: str = Field(default="")
    """System prompt"""

    @model_validator(mode="after")
    def validate_system_prompt(self):
        if self.system_prompt is None or (
            isinstance(self.system_prompt, str)
            and (self.system_prompt == "" or self.system_prompt.strip() == "")
        ):
            self.system_prompt = SystemPrompts(model_id=self.modelId).VideoAnalysisSysPrompt
        return self

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

    top_p: float = Field(default=0.9)
    """Top-p sampling parameter.
    Ranges from 0.0 to 1.0
    """

    top_k: int = Field(default=50)
    """Top-k sampling parameter.
    """

    frame_interval: float = Field(default=1.0)
    """Interval between frames in seconds"""

    max_frames: int = Field(default=20)
    """Maximum number of frames to extract"""

    use_converse_api: bool = Field(default=False)
    """Whether to use `converse` API or not
    defaults to `invoke_model` API
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse.html
    """

    enable_cri: bool = Field(default=False)
    """Whether to use Cross-region inference (CRI) or not
    Some models may only be available via `inference_profiles` for CRI
    https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html
    """

    s3_bucket_owner: Optional[str] = Field(default=None)
    """AWS account ID of the S3 bucket owner.
    Required for cross-account S3 access with Nova models.
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

        # Check if the model is a Nova model (only Nova models are supported for video analysis)
        model_id = values.get("modelId")

        # Set default model if not provided
        if model_id is None:
            model_id = LanguageModels.NOVA_LITE
            values["modelId"] = model_id

        if model_id not in [LanguageModels.NOVA_PRO, LanguageModels.NOVA_LITE]:
            logger.error(
                f"Video analysis is only supported with Nova models (NOVA_PRO or NOVA_LITE). Selected model: {model_id.name}"
            )
            raise ValueError(
                f"Video analysis is only supported with Nova models (NOVA_PRO or NOVA_LITE). "
                f"Selected model: {model_id.name}"
            )

        # For local files, we'll need to upload to S3 (not implemented in this version)
        if not file_path.startswith("s3://"):
            logger.error("Video analysis currently only supports videos stored in S3.")
            raise ValueError(
                "Video analysis currently only supports videos stored in S3. "
                "Please upload your video to S3 and provide the S3 URI."
            )

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

    def _parse_s3_path(self, s3_path: str) -> Tuple[str, str]:
        """
        Parse the S3 file path and extract the bucket name and key.

        Args:
            s3_path (str): The S3 file path.

        Returns:
            Tuple[str, str]: A tuple containing the bucket name and key.
        """
        parts = s3_path[5:].partition("/")
        bucket_name = parts[0]
        key = parts[2]
        return bucket_name, key

    def _get_video_format(self) -> str:
        """
        Get the video format from the file path.

        Returns:
            str: Video format (e.g., 'mp4', 'avi', etc.)
        """
        mime_type, _ = mimetypes.guess_type(self.file_path)
        if mime_type and mime_type.startswith("video/"):
            return mime_type.split("/")[-1]
        # Default to mp4 if can't determine
        return "mp4"

    def _get_request_body(
        self,
        message: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        output_schema: Optional[dict] = None,
    ) -> Dict:
        """
        Prepare the request body for the API call.

        Args:
            message (str): Message/query about the video.
            max_tokens (Optional[int]): Override the default max_tokens value.
            temperature (Optional[float]): Override the default temperature value.
            top_p (Optional[float]): Override the default top_p value.
            top_k (Optional[int]): Override the default top_k value.
            output_schema (Optional[dict]): The output schema for structured responses.

        Returns:
            Dict: The request body for the API call.
        """
        # Create messages with direct S3 reference
        system_list = [{"text": self.system_prompt}]

        # Parse S3 path
        video_format = self._get_video_format()

        # Create S3 location object
        s3_location = {"uri": self.file_path}

        # Add bucket owner if provided
        if self.s3_bucket_owner:
            s3_location["bucketOwner"] = self.s3_bucket_owner

        # Create message with video reference
        message_list = [
            {
                "role": "user",
                "content": [
                    {"video": {"format": video_format, "source": {"s3Location": s3_location}}},
                    {"text": message},
                ],
            }
        ]

        # Configure inference parameters with overrides if provided
        inf_params = {
            "maxTokens": max_tokens if max_tokens is not None else self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
            "topP": top_p if top_p is not None else self.top_p,
        }

        # Add topK only for invoke_model API (not for converse API)
        if not self.use_converse_api:
            inf_params["topK"] = top_k if top_k is not None else self.top_k

        # Create the request body with the correct schema
        body = {
            "schemaVersion": "messages-v1",
            "messages": message_list,
            "system": system_list,
            "inferenceConfig": inf_params,
        }

        return body

    def run(
        self,
        message: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        output_schema: Optional[dict] = None,
    ) -> Any:
        """
        Run video analysis with the given message.

        Args:
            message (str): Message/query about the video.
            max_tokens (Optional[int]): Override the default max_tokens value.
            temperature (Optional[float]): Override the default temperature value.
            top_p (Optional[float]): Override the default top_p value.
            top_k (Optional[int]): Override the default top_k value.
            output_schema (Optional[dict]): The output schema for structured responses.

        Returns:
            Dict[str, Any]: Response from the model.
        """
        # Prepare the request body
        body = self._get_request_body(
            message=message,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            output_schema=output_schema,
        )

        # Use the Invocations class for API calls
        model_invoke = Invocations(
            body=body,
            bedrock_client=self._bedrock_client,
            boto3_session=self.boto3_session,
            model_id=self.modelId.value,
            output_schema=output_schema,
            use_converse_api=self.use_converse_api,
            enable_cri=self.enable_cri,
        )

        response = model_invoke.run_inference()
        self._message_history = model_invoke.message_history

        # Add video path to the response
        if isinstance(response, dict):
            response["video_path"] = self.file_path

        return response

    def run_stream(
        self,
        message: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Run video analysis with the given message and stream the response.

        Args:
            message (str): Message/query about the video.
            max_tokens (Optional[int]): Override the default max_tokens value.
            temperature (Optional[float]): Override the default temperature value.
            top_p (Optional[float]): Override the default top_p value.
            top_k (Optional[int]): Override the default top_k value.

        Yields:
            Dict[str, Any]: Streaming response from the model.
        """
        # Prepare the request body
        body = self._get_request_body(
            message=message,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
        )

        # Convert to JSON string for the API call
        body_str = json.dumps(body)

        # Make direct API call to bedrock-runtime with streaming
        response_stream = self._bedrock_client.invoke_model_with_response_stream(
            modelId=self.modelId.value, body=body_str
        )

        # Process the streaming response
        collected_response = ""
        for event in response_stream["body"]:
            if "chunk" in event:
                chunk_data = json.loads(event["chunk"]["bytes"].decode())

                # Handle contentBlockDelta chunks which contain the actual text
                if "contentBlockDelta" in chunk_data:
                    text_content = chunk_data["contentBlockDelta"]["delta"].get("text", "")
                    if text_content:
                        collected_response += text_content
                        yield {"response": text_content, "collected_response": collected_response}

                # You can also handle other chunk types if needed
                elif "messageStop" in chunk_data:
                    # This indicates the end of the message
                    yield {
                        "status": "complete",
                        "reason": chunk_data["messageStop"].get("stopReason", "unknown"),
                    }

        # Update message history
        if body.get("messages"):
            messages = body["messages"]
            messages.append({"role": "assistant", "content": [{"text": collected_response}]})
            self._message_history = messages
