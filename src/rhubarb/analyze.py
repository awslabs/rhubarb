# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, Dict, List, Optional, Generator

from pydantic import Field, BaseModel, PrivateAttr, validator, model_validator
from botocore.config import Config

from rhubarb.models import LanguageModels
from rhubarb.invocations import Invocations
from rhubarb.user_prompts import UserMessages
from rhubarb.file_converter import LargeDocumentProcessor
from rhubarb.system_prompts import SystemPrompts

logger = logging.getLogger(__name__)


class DocAnalysis(BaseModel):
    """
    Analyzes a document using the specified Bedrock Language Model.

    Args:
    - `file_path` (str): File path of the document, local or S3 path.
    - `modelId` (LanguageModels, optional): Bedrock Model ID. Defaults to LanguageModels.CLAUDE_SONNET_V2.
    - `system_prompt` (str, optional): System prompt. Defaults to SystemPrompts().DefaultSysPrompt.
    - `boto3_session` (Any): Instance of boto3.session.Session.
    - `max_tokens` (int, optional): The maximum number of tokens to generate before stopping. Max 4096 tokens for Claude models. Defaults to 1024.
    - `temperature` (int, optional): Amount of randomness injected into the response. Ranges from 0.0 to 1.0. Defaults to 0.
    - `pages` (List[int], optional): Pages of a multi-page PDF or TIF to process. [0] will process all pages upto 20 pages max,
    [1,3,5] will process pages 1, 3 and 5. Defaults to [0].
    - `use_converse_api` (bool, optional): Use Bedrock `converse` API to enable tool use. Defaults to `False` and uses `invoke_model`.
    - `enable_cri` (bool, optional): Enables Cross-region inference for certain models. Defaults to `False`.
    - `sliding_window_overlap` (int, optional): Number of pages to overlap between windows when using sliding window. 0 disables sliding window, 1-10 enables it. Defaults to 0.

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

    modelId: LanguageModels = Field(default=LanguageModels.CLAUDE_SONNET_V2)
    """Bedrock Model ID"""

    system_prompt: str = Field(default="")
    """System prompt"""

    @validator("system_prompt", pre=True, always=True)
    def set_system_prompt(cls, v, values):
        return SystemPrompts(
            model_id=values.get("modelId", LanguageModels.CLAUDE_SONNET_V2)
        ).DefaultSysPrompt

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

    sliding_window_overlap: int = Field(default=0)
    """Number of pages to overlap between windows when using sliding window
    - 0: Sliding window is disabled
    - 1-10: Number of pages to overlap between windows
    - Values > 10 are not allowed
    """

    _message_history: List[Any] = PrivateAttr(default=None)
    """History of user/assistant messages"""

    _bedrock_client: Any = PrivateAttr(default=None)
    """boto3 bedrock-runtime client, will get overriten by boto3_session"""

    _s3_client: Any = PrivateAttr(default=None)
    """boto3 s3 client, will get overriten by boto3_session"""

    _large_doc_processor: Any = PrivateAttr(default=None)
    """LargeDocumentProcessor instance for handling documents with more than 20 pages"""

    def _initialize_large_doc_processor(self):
        """
        Initialize the LargeDocumentProcessor if not already initialized.
        """
        # Validate sliding_window_overlap
        if self.sliding_window_overlap > 10:
            raise ValueError("sliding_window_overlap cannot be greater than 10")

        # Initialize if sliding window is enabled (overlap > 0)
        if self._large_doc_processor is None and self.sliding_window_overlap > 0:
            self._large_doc_processor = LargeDocumentProcessor(
                file_path=self.file_path, s3_client=self._s3_client
            )

    def _process_with_sliding_window(
        self, message: str, output_schema: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Process a document using the sliding window approach.

        Args:
            message (str): The message to send to the model.
            output_schema (Optional[dict], optional): The output schema. Defaults to None.

        Returns:
            Dict[str, Any]: The combined results from all windows.
        """
        self._initialize_large_doc_processor()

        # Define the processor function that will be called for each window
        def process_window(page_data, **kwargs):
            window_info = kwargs.get("window_info", {})
            window_message = f"{message}\n\nNote: You are currently viewing pages {window_info['current_window_start']} to {window_info['current_window_end']} of {window_info['total_pages']} total pages."

            # Construct the body for the API call
            body = {}

            if self.use_converse_api:
                # For converse API
                content = []
                for page in page_data:
                    content.append({"text": f"Page: {page['page']}"})
                    content.append(
                        {"image": {"format": "png", "source": {"bytes": page["image_bytes"]}}}
                    )
                content.append({"text": window_message})

                messages = [{"role": "user", "content": content}]
                body["messages"] = messages
                body["system"] = [{"text": self.system_prompt}]
                body["inferenceConfig"] = {
                    "maxTokens": self.max_tokens,
                    "temperature": self.temperature,
                }
            else:
                # For invoke_model API
                if str(self.modelId).__contains__("NOVA"):
                    # Nova format
                    content = []
                    content.append({"text": window_message})

                    # Add images from pages
                    for page in page_data:
                        content.append(
                            {"image": {"format": "png", "source": {"bytes": page["base64string"]}}}
                        )

                    messages = [{"role": "user", "content": content}]
                    body["messages"] = messages
                    body["system"] = [{"text": self.system_prompt}]
                else:
                    # Claude format
                    content = []
                    for page in page_data:
                        content.append({"type": "text", "text": f"Page: {page['page']}"})
                        content.append(
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": page["base64string"],
                                },
                            }
                        )
                    content.append({"type": "text", "text": window_message})

                    messages = [{"role": "user", "content": content}]
                    body["messages"] = messages
                    body["system"] = self.system_prompt
                    body["max_tokens"] = self.max_tokens
                    body["temperature"] = self.temperature
                    body["anthropic_version"] = "bedrock-2023-05-31"

            # Invoke the model
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

            # Add window info to the response
            if isinstance(response, dict):
                response["window_info"] = window_info

            return response

        # Process the document using the sliding window approach
        results = self._large_doc_processor.process_document(
            processor_func=process_window,
            use_converse_api=self.use_converse_api,
            overlap=self.sliding_window_overlap,
        )

        # If there are multiple windows, add a synthesis step
        if len(results) > 1:
            synthesized_result = self._synthesize_window_results(results, message, output_schema)
            return {"synthesized_response": synthesized_result, "window_results": results}

        # If there's only one window, just return its result
        if len(results) == 1:
            return results[0]

        # Combine the results (fallback for empty results)
        combined_result = self._combine_window_results(results)

        return combined_result

    def _combine_window_results(self, results: List[Any]) -> Dict[str, Any]:
        """
        Combine the results from multiple windows into a single result.

        Args:
            results (List[Any]): List of results from each window.

        Returns:
            Dict[str, Any]: The combined result.
        """
        if not results:
            return {}

        # If the results are strings, concatenate them
        if all(isinstance(r, str) for r in results):
            combined_text = ""
            for i, result in enumerate(results):
                window_info = results[i].get("window_info", {})
                start_page = window_info.get("current_window_start", "unknown")
                end_page = window_info.get("current_window_end", "unknown")
                combined_text += f"Pages {start_page}-{end_page}:\n{result}\n\n"
            return combined_text

        # If the results are dictionaries, merge them
        if all(isinstance(r, dict) for r in results):
            combined = {}

            # Add metadata about the sliding window processing
            combined["sliding_window_processing"] = {
                "total_windows": len(results),
                "window_info": [r.get("window_info", {}) for r in results],
            }

            # For each result, add its content to the combined result
            for i, result in enumerate(results):
                window_info = result.get("window_info", {})
                window_range = f"{window_info.get('current_window_start', 'unknown')}-{window_info.get('current_window_end', 'unknown')}"

                # Remove window_info from the result to avoid duplication
                result_copy = result.copy()
                if "window_info" in result_copy:
                    del result_copy["window_info"]

                # Add the result to the combined result
                combined[f"window_{i+1}_pages_{window_range}"] = result_copy

            return combined

        # If the results are of mixed types, return them as a list
        return {"windows": results}

    def _synthesize_window_results(
        self, results: List[Any], original_message: str, output_schema: Optional[dict] = None
    ) -> Any:
        """
        Synthesize results from multiple windows into a coherent response.

        Args:
            results (List[Any]): List of results from each window.
            original_message (str): The original message/question.
            output_schema (Optional[dict], optional): The output schema. Defaults to None.

        Returns:
            Any: The synthesized result.
        """
        # Prepare a summary of each window's results
        window_summaries = []

        for i, result in enumerate(results):
            window_info = result.get("window_info", {})
            start_page = window_info.get("current_window_start", "unknown")
            end_page = window_info.get("current_window_end", "unknown")

            # Format the result for inclusion in the synthesis prompt
            if isinstance(result, dict):
                # Remove window_info to avoid clutter
                result_copy = result.copy()
                if "window_info" in result_copy:
                    del result_copy["window_info"]

                # Convert to string representation
                import json

                result_str = json.dumps(result_copy, indent=2)
            else:
                result_str = str(result)

            window_summary = f"Window {i+1} (Pages {start_page}-{end_page}):\n{result_str}"
            window_summaries.append(window_summary)

        # Create a synthesis prompt
        synthesis_prompt = f"""
        I've analyzed a document in {len(results)} sections and found information related to your question.
        
        Your question was: "{original_message}"
        
        Here are the results from each section:
        
        {"\n\n".join(window_summaries)}
        
        Please provide a direct, concise answer to the question based on the information found. 
        Focus ONLY on the sections that contain relevant information - do not mention sections that don't have relevant information.
        
        If the answer is found in only one section, simply provide that answer without discussing other sections.
        If multiple sections contain relevant information, synthesize it into a single coherent response.
        If no sections contain relevant information, state that the document does not contain information about the topic.
        
        Be direct and to the point in your response.
        """

        # Create a system prompt for synthesis
        synthesis_system_prompt = """
        You are an expert at synthesizing information from document sections.
        Your task is to provide direct, concise answers based on the information found.
        
        Guidelines:
        1. Focus ONLY on sections that contain relevant information
        2. Do not mention sections that don't have relevant information
        3. Be direct and to the point - users want clear answers, not analysis of the document structure
        4. If the answer is only in one section, just provide that answer
        5. If multiple sections have relevant information, combine it coherently
        6. If no sections have relevant information, clearly state that
        
        Avoid phrases like "Based on the sections provided" or "According to the document sections" - 
        just provide the answer directly as if you're answering the question yourself.
        """

        # Make the synthesis call
        a_msg = UserMessages(
            file_path=self.file_path,
            s3_client=self._s3_client,
            system_prompt=synthesis_system_prompt,
            message=synthesis_prompt,
            output_schema=output_schema,
            max_tokens=self.max_tokens * 2,  # Allow more tokens for synthesis
            temperature=self.temperature,
            pages=[],  # No pages needed for synthesis
            use_converse_api=False,  # Always use invoke_model for synthesis
            modelId=self.modelId,
        )

        body = a_msg.messages()

        model_invoke = Invocations(
            body=body,
            bedrock_client=self._bedrock_client,
            boto3_session=self.boto3_session,
            model_id=self.modelId.value,
            output_schema=output_schema,
            use_converse_api=False,
            enable_cri=self.enable_cri,
        )

        synthesis_response = model_invoke.run_inference()
        return synthesis_response

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, values: dict) -> dict:
        file_path = values.get("file_path")
        pages = values.get("pages", [0])

        if 0 in pages and len(pages) > 1:
            logger.error("If specific pages are provided, page number 0 is invalid.")
            raise ValueError("If specific pages are provided, page number 0 is invalid.")

        if len(pages) > 20 and values.get("sliding_window_overlap", 0) <= 0:
            logger.error(
                "Cannot process more than 20 pages at a time without enabling sliding window (set sliding_window_overlap > 0)."
            )
            raise ValueError(
                "Cannot process more than 20 pages at a time without enabling sliding window (set sliding_window_overlap > 0)."
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

    def _get_user_prompt(
        self,
        message: Any,
        sys_prompt: str,
        output_schema: Optional[dict] = None,
        history: Optional[List[dict]] = None,
    ) -> Any:
        return UserMessages(
            file_path=self.file_path,
            s3_client=self._s3_client,
            system_prompt=sys_prompt,
            message=message,
            output_schema=output_schema,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            pages=self.pages,
            use_converse_api=self.use_converse_api,
            message_history=history,
            modelId=self.modelId,
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
        # If sliding window is enabled and we're not using history, use the sliding window approach
        if self.sliding_window_overlap > 0 and not history:
            return self._process_with_sliding_window(message, output_schema)

        if (
            self.modelId == LanguageModels.CLAUDE_HAIKU_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V2
            or self.modelId == LanguageModels.NOVA_LITE
            or self.modelId == LanguageModels.NOVA_PRO
        ):
            # sys_prompt = SystemPrompts(model_id=self.modelId).DefaultSysPrompt
            a_msg = self._get_user_prompt(
                message=message,
                output_schema=output_schema,
                sys_prompt=self.system_prompt,
                history=history,
            )
            body = a_msg.messages()

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
        return response

    def run_stream(
        self, message: Any, history: Optional[List[dict]] = None
    ) -> Generator[Any, Any, Any]:
        """
        Invokes the specified language model with the given message in streaming mode.

        Args:
        - `message` (`Any`): The input message or prompt for the language model.
        """
        # Streaming mode doesn't support sliding window approach
        if self.sliding_window_overlap > 0:
            logger.warning(
                "Sliding window approach is not supported in streaming mode. Using standard approach."
            )

        if (
            self.modelId == LanguageModels.CLAUDE_OPUS_V1
            or self.modelId == LanguageModels.CLAUDE_HAIKU_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V2
            or self.modelId == LanguageModels.NOVA_LITE
            or self.modelId == LanguageModels.NOVA_PRO
        ):
            a_msg = self._get_user_prompt(
                message=message, sys_prompt=self.system_prompt, history=history
            )
            body = a_msg.messages()

        model_invoke = Invocations(
            body=body,
            bedrock_client=self._bedrock_client,
            boto3_session=self.boto3_session,
            model_id=self.modelId.value,
            use_converse_api=self.use_converse_api,
            enable_cri=self.enable_cri,
        )
        for response in model_invoke.run_inference_stream():
            yield response
        self._message_history = model_invoke.message_history

    def run_entity(self, message: Any, entities: List[Any]) -> Any:
        """
        Invokes the specified language model with the given message in streaming mode.

        Args:
        - `message` (`Any`): The input message or prompt for the language model.
        - `entities` (`List[Entities.entity]`): A list of entities to be detected
        """
        # Entity extraction doesn't support sliding window approach
        if self.sliding_window_overlap > 0:
            logger.warning(
                "Sliding window approach is not supported for entity extraction. Using standard approach."
            )

        if (
            self.modelId == LanguageModels.CLAUDE_OPUS_V1
            or self.modelId == LanguageModels.CLAUDE_HAIKU_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V2
            or self.modelId == LanguageModels.NOVA_LITE
            or self.modelId == LanguageModels.NOVA_PRO
        ):
            sys_prompt = SystemPrompts(entities=entities, model_id=self.modelId).NERSysPrompt
            a_msg = self._get_user_prompt(message=message, sys_prompt=sys_prompt)
            body = a_msg.messages()

        model_invoke = Invocations(
            body=body,
            bedrock_client=self._bedrock_client,
            boto3_session=self.boto3_session,
            model_id=self.modelId.value,
            use_converse_api=self.use_converse_api,
            enable_cri=self.enable_cri,
        )
        response = model_invoke.run_inference()
        return response

    def generate_schema(self, message: str, assistive_rephrase: Optional[bool] = False) -> dict:
        """
        Invokes the specified language model with the given message to generate a JSON
        schema for a given document.

        Args:
        - `message` (`Any`): The input message or prompt for the language model.
        - `assistive_rephrase` (`bool`): If set to true, will rephrase the question properly for subsequent use
        """
        # Schema generation doesn't support sliding window approach
        if self.sliding_window_overlap > 0:
            logger.warning(
                "Sliding window approach is not supported for schema generation. Using standard approach."
            )

        if (
            self.modelId == LanguageModels.CLAUDE_OPUS_V1
            or self.modelId == LanguageModels.CLAUDE_HAIKU_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V1
            or self.modelId == LanguageModels.CLAUDE_SONNET_V2
            or self.modelId == LanguageModels.NOVA_LITE
            or self.modelId == LanguageModels.NOVA_PRO
        ):
            if assistive_rephrase:
                sys_prompt = SystemPrompts(model_id=self.modelId).SchemaGenSysPromptWithRephrase
            else:
                sys_prompt = SystemPrompts(model_id=self.modelId).SchemaGenSysPrompt
            a_msg = self._get_user_prompt(message=message, sys_prompt=sys_prompt)
            body = a_msg.messages()

        model_invoke = Invocations(
            body=body,
            bedrock_client=self._bedrock_client,
            boto3_session=self.boto3_session,
            model_id=self.modelId.value,
            use_converse_api=self.use_converse_api,
            enable_cri=self.enable_cri,
        )
        response = model_invoke.run_inference()
        return response
