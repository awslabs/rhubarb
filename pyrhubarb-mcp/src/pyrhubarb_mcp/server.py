# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Rhubarb FastMCP Server Implementation

This module provides a FastMCP server that exposes all of Rhubarb's document and video
understanding capabilities through tools and resources.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Union
import uuid

import boto3
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from rhubarb import DocAnalysis, DocClassification, VideoAnalysis
from rhubarb.models import LanguageModels, EmbeddingModels
from rhubarb.schema_factory.entities import Entities


# Model mapping from friendly names to Rhubarb enum values
MODEL_MAPPING = {
    'claude-opus': LanguageModels.CLAUDE_OPUS_V1,
    'claude-sonnet': LanguageModels.CLAUDE_SONNET_V2,
    'claude-sonnet-v1': LanguageModels.CLAUDE_SONNET_V1,
    'claude-sonnet-v2': LanguageModels.CLAUDE_SONNET_V2,
    'claude-sonnet-37': LanguageModels.CLAUDE_SONNET_37,
    'claude-haiku': LanguageModels.CLAUDE_HAIKU_V1,
    'nova-pro': LanguageModels.NOVA_PRO,
    'nova-lite': LanguageModels.NOVA_LITE
}

# Built-in entity types for NER
BUILT_IN_ENTITIES = [
    'PERSON', 'ORGANIZATION', 'LOCATION', 'DATE', 'TIME', 'MONEY', 'PERCENT',
    'EMAIL', 'PHONE_NUMBER', 'URL', 'CREDIT_CARD', 'SSN', 'PASSPORT',
    'DRIVER_LICENSE', 'ADDRESS', 'BANK_ACCOUNT', 'ROUTING_NUMBER',
    'IP_ADDRESS', 'MAC_ADDRESS', 'USERNAME', 'PASSWORD', 'API_KEY',
    'MEDICAL_RECORD_NUMBER', 'PATIENT_ID', 'INSURANCE_NUMBER',
    'LICENSE_PLATE', 'VIN', 'SERIAL_NUMBER', 'ISBN', 'PRODUCT_CODE',
    'CONTRACT_NUMBER', 'INVOICE_NUMBER', 'ORDER_NUMBER', 'CASE_NUMBER',
    'REFERENCE_NUMBER', 'TRACKING_NUMBER', 'CONFIRMATION_CODE',
    'RESERVATION_NUMBER', 'MEMBERSHIP_NUMBER', 'EMPLOYEE_ID',
    'CUSTOMER_ID', 'VENDOR_ID', 'TRANSACTION_ID', 'SESSION_ID',
    'REQUEST_ID', 'TICKET_NUMBER', 'POLICY_NUMBER', 'CLAIM_NUMBER',
    'ACCOUNT_NUMBER', 'CERTIFICATE_NUMBER', 'PERMIT_NUMBER',
    'APPLICATION_NUMBER', 'REGISTRATION_NUMBER', 'TAX_ID'
]

# Built-in schema types
BUILT_IN_SCHEMAS = {
    'ner': 'Named Entity Recognition schema',
    'classification': 'Document classification schema',
    'figures': 'Figure and chart understanding schema',
    'pii': 'Personally Identifiable Information schema',
    'chat': 'Chat and Q&A schema',
    'default': 'Default document analysis schema',
    'multiclass': 'Multi-class classification schema',
    'sample': 'Sample extraction schema'
}

# Global conversation storage
conversations: Dict[str, List[Any]] = {}


class RhubarbMCPServer:
    """FastMCP server for Rhubarb document and video understanding capabilities."""

    def __init__(self):
        self.mcp = FastMCP("Rhubarb Server")
        self._setup_tools()
        self._setup_resources()

    def _get_boto3_session(self) -> boto3.Session:
        """Get boto3 session with configured credentials."""
        return boto3.Session()

    def _generate_conversation_id(self) -> str:
        """Generate a unique conversation ID."""
        return f"conv_{int(asyncio.get_event_loop().time() * 1000)}_{uuid.uuid4().hex[:8]}"

    def _setup_tools(self):
        """Register all MCP tools."""

        # Document Analysis Tools
        @self.mcp.tool()
        def analyze_document(
            file_path: str,
            message: str,
            model: str = "claude-sonnet",
            pages: Optional[List[int]] = None,
            output_schema: Optional[Dict] = None,
            sliding_window_overlap: int = 0,
            max_tokens: int = 1024,
            temperature: float = 0.0
        ) -> Dict[str, Any]:
            """
            Analyze a document using multi-modal AI models for Q&A, summarization, or extraction.
            
            Args:
                file_path: Local or S3 path to document
                message: Question or instruction for analysis
                model: Model to use for analysis (claude-sonnet, claude-haiku, nova-pro, etc.)
                pages: Specific pages to analyze (optional)
                output_schema: JSON schema for structured extraction (optional)
                sliding_window_overlap: Enable large document processing (0 disables, 1-10 enables)
                max_tokens: Maximum tokens to generate
                temperature: Randomness in response (0-1)
            """
            try:
                if model not in MODEL_MAPPING:
                    return {"error": f"Invalid model: {model}. Available models: {list(MODEL_MAPPING.keys())}"}

                session = self._get_boto3_session()
                da = DocAnalysis(
                    file_path=file_path,
                    modelId=MODEL_MAPPING[model],
                    boto3_session=session,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    pages=pages or [0],
                    sliding_window_overlap=sliding_window_overlap,
                    enable_cri=os.getenv('RHUBARB_ENABLE_CRI', 'false').lower() == 'true'
                )

                result = da.run(message=message, output_schema=output_schema)
                
                return {
                    "success": True,
                    "result": result,
                    "model_used": model,
                    "file_path": file_path
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }

        @self.mcp.tool()
        def stream_document_chat(
            file_path: str,
            message: str,
            conversation_id: Optional[str] = None,
            model: str = "claude-sonnet"
        ) -> Dict[str, Any]:
            """
            Start a streaming conversation with a document.
            
            Args:
                file_path: Local or S3 path to document
                message: Message for the conversation
                conversation_id: ID to maintain conversation history (optional)
                model: Model to use for chat
            """
            try:
                if model not in MODEL_MAPPING:
                    return {"error": f"Invalid model: {model}"}

                conv_id = conversation_id or self._generate_conversation_id()
                history = conversations.get(conv_id, [])

                session = self._get_boto3_session()
                da = DocAnalysis(
                    file_path=file_path,
                    modelId=MODEL_MAPPING[model],
                    boto3_session=session,
                    enable_cri=os.getenv('RHUBARB_ENABLE_CRI', 'false').lower() == 'true'
                )

                # Collect streaming results
                collected_response = ""
                for chunk in da.run_stream(message=message, history=history if history else None):
                    collected_response += str(chunk)

                # Update conversation history
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": collected_response})
                conversations[conv_id] = history

                return {
                    "success": True,
                    "result": collected_response,
                    "conversation_id": conv_id,
                    "streaming": True
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }

        @self.mcp.tool()
        def extract_entities(
            file_path: str,
            entity_types: Optional[List[str]] = None,
            custom_entities: Optional[List[str]] = None,
            extract_pii: bool = False
        ) -> Dict[str, Any]:
            """
            Extract named entities or PII from a document.
            
            Args:
                file_path: Local or S3 path to document
                entity_types: Types of entities to extract
                custom_entities: Custom entity definitions
                extract_pii: Extract PII entities
            """
            try:
                # Build entity list
                entities = list(entity_types or [])
                if extract_pii:
                    entities.extend(['EMAIL', 'PHONE_NUMBER', 'SSN', 'CREDIT_CARD', 'ADDRESS'])
                entities.extend(custom_entities or [])

                if not entities:
                    entities = ['PERSON', 'ORGANIZATION', 'LOCATION', 'DATE']

                session = self._get_boto3_session()
                da = DocAnalysis(
                    file_path=file_path,
                    modelId=LanguageModels.CLAUDE_SONNET_V2,
                    boto3_session=session,
                    enable_cri=os.getenv('RHUBARB_ENABLE_CRI', 'false').lower() == 'true'
                )

                # Map entity types to Rhubarb entities
                entity_objects = []
                entities_class = Entities()

                for entity_name in entities:
                    if hasattr(entities_class, entity_name.lower()):
                        entity_objects.append(getattr(entities_class, entity_name.lower()))
                    else:
                        # Create custom entity
                        custom_entity = type('Entity', (), {
                            'name': entity_name,
                            'description': f'Custom entity: {entity_name}'
                        })()
                        entity_objects.append(custom_entity)

                result = da.run_entity(
                    message="Extract all entities from this document",
                    entities=entity_objects
                )

                return {
                    "success": True,
                    "result": result,
                    "entities_requested": entities
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }

        @self.mcp.tool()
        def generate_extraction_schema(
            file_path: str,
            extraction_description: str,
            assistive_rephrase: bool = False
        ) -> Dict[str, Any]:
            """
            Generate a JSON schema for structured data extraction from documents.
            
            Args:
                file_path: Sample document path
                extraction_description: Description of data to extract
                assistive_rephrase: Improve the extraction prompt
            """
            try:
                session = self._get_boto3_session()
                da = DocAnalysis(
                    file_path=file_path,
                    modelId=LanguageModels.CLAUDE_SONNET_V2,
                    boto3_session=session,
                    enable_cri=os.getenv('RHUBARB_ENABLE_CRI', 'false').lower() == 'true'
                )

                result = da.generate_schema(
                    message=extraction_description,
                    assistive_rephrase=assistive_rephrase
                )

                return {
                    "success": True,
                    "result": result,
                    "description": extraction_description
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }

        # Classification Tools
        @self.mcp.tool()
        def create_classification_samples(
            manifest_path: str,
            bucket_name: str,
            update_sample_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Create vector samples for document classification from a manifest file.
            
            Args:
                manifest_path: Path to CSV manifest with training samples
                bucket_name: S3 bucket for storing vector samples
                update_sample_id: ID of existing samples to update (optional)
            """
            try:
                session = self._get_boto3_session()
                dc = DocClassification(
                    bucket_name=bucket_name,
                    boto3_session=session
                )

                result = dc.run_sampling(
                    manifest_path=manifest_path,
                    update_sample_id=update_sample_id
                )

                return {
                    "success": True,
                    "result": result
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }

        @self.mcp.tool()
        def classify_document(
            file_path: str,
            sample_id: str,
            bucket_name: str,
            similarity_metric: str = "cosine",
            top_n: int = 1,
            unknown_threshold: float = 0.8,
            pages: Optional[List[int]] = None
        ) -> Dict[str, Any]:
            """
            Classify a document using pre-trained vector samples.
            
            Args:
                file_path: Document to classify
                sample_id: Classification sample ID
                bucket_name: S3 bucket containing samples
                similarity_metric: Similarity metric (cosine or l2)
                top_n: Number of top classes to return
                unknown_threshold: Threshold for unknown classification
                pages: Pages to classify
            """
            try:
                session = self._get_boto3_session()
                dc = DocClassification(
                    bucket_name=bucket_name,
                    boto3_session=session
                )

                result = dc.run_classify(
                    sample_id=sample_id,
                    file_path=file_path,
                    pages=pages or [0],
                    similarity_metric=similarity_metric,
                    top_n=top_n,
                    unknown_threshold=unknown_threshold
                )

                return {
                    "success": True,
                    "result": result
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }

        @self.mcp.tool()
        def view_classification_sample(
            sample_id: str,
            bucket_name: str
        ) -> Dict[str, Any]:
            """
            View details of a classification sample set.
            
            Args:
                sample_id: Classification sample ID to view
                bucket_name: S3 bucket containing samples
            """
            try:
                session = self._get_boto3_session()
                dc = DocClassification(
                    bucket_name=bucket_name,
                    boto3_session=session
                )

                result = dc.view_sample(sample_id=sample_id)

                return {
                    "success": True,
                    "result": result
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }

        # Video Analysis Tools
        @self.mcp.tool()
        def analyze_video(
            file_path: str,
            message: str,
            model: str = "nova-lite",
            frame_interval: float = 1.0,
            max_frames: int = 20,
            s3_bucket_owner: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Analyze video content using Amazon Nova models.
            
            Args:
                file_path: S3 path to video file (required)
                message: Question or instruction about the video
                model: Nova model to use (nova-pro or nova-lite)
                frame_interval: Interval between frames in seconds
                max_frames: Maximum frames to extract
                s3_bucket_owner: AWS account ID for cross-account access (optional)
            """
            try:
                if model not in ['nova-pro', 'nova-lite']:
                    return {
                        "error": f"Invalid video model: {model}. Only nova-pro and nova-lite are supported."
                    }

                if not file_path.startswith('s3://'):
                    return {"error": "Video analysis requires S3 storage. File must be uploaded to S3."}

                session = self._get_boto3_session()
                va = VideoAnalysis(
                    file_path=file_path,
                    modelId=MODEL_MAPPING[model],
                    boto3_session=session,
                    frame_interval=frame_interval,
                    max_frames=max_frames,
                    s3_bucket_owner=s3_bucket_owner,
                    enable_cri=os.getenv('RHUBARB_ENABLE_CRI', 'false').lower() == 'true'
                )

                result = va.run(message=message)

                return {
                    "success": True,
                    "result": result
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }

    def _setup_resources(self):
        """Register all MCP resources."""

        @self.mcp.resource("rhubarb://entities/built-in")
        def get_built_in_entities() -> str:
            """Get the list of built-in entity types for Named Entity Recognition."""
            return json.dumps({
                "entities": BUILT_IN_ENTITIES,
                "count": len(BUILT_IN_ENTITIES),
                "description": "Built-in entity types supported by Rhubarb for Named Entity Recognition"
            }, indent=2)

        @self.mcp.resource("rhubarb://models/supported")
        def get_supported_models() -> str:
            """Get the list of supported Bedrock models and their capabilities."""
            models = []
            for friendly_name, model_enum in MODEL_MAPPING.items():
                models.append({
                    "friendly_name": friendly_name,
                    "rhubarb_enum": model_enum.name,
                    "supports_documents": True,
                    "supports_video": friendly_name.startswith('nova-'),
                    "max_tokens": 4096,
                    "multimodal": True
                })

            return json.dumps({
                "models": models,
                "default_model": os.getenv('RHUBARB_DEFAULT_MODEL', 'claude-sonnet')
            }, indent=2)

        @self.mcp.resource("rhubarb://schemas/built-in/{schema_type}")
        def get_built_in_schema(schema_type: str) -> str:
            """Get built-in JSON schemas for common document processing use cases."""
            if schema_type not in BUILT_IN_SCHEMAS:
                raise ValueError(f"Unknown schema type: {schema_type}")

            return json.dumps({
                "schema_type": schema_type,
                "description": BUILT_IN_SCHEMAS[schema_type],
                "note": "This is a reference to built-in schemas. Use generate_extraction_schema tool to create custom schemas."
            }, indent=2)

        @self.mcp.resource("rhubarb://classification-samples/{bucket}/{sample_id}")
        def get_classification_sample(bucket: str, sample_id: str) -> str:
            """Get details of classification sample sets including classes and sample counts."""
            try:
                session = self._get_boto3_session()
                dc = DocClassification(
                    bucket_name=bucket,
                    boto3_session=session
                )

                result = dc.view_sample(sample_id=sample_id)
                return json.dumps(result, indent=2, default=str)

            except Exception as e:
                return json.dumps({
                    "error": str(e),
                    "error_type": type(e).__name__
                }, indent=2)


def create_server() -> FastMCP:
    """Create and return a configured Rhubarb FastMCP server."""
    server = RhubarbMCPServer()
    return server.mcp


async def run_server():
    """Run the Rhubarb FastMCP server."""
    server = create_server()
    await server.run()


if __name__ == "__main__":
    asyncio.run(run_server())
