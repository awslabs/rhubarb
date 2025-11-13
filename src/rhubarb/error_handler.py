# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Error handling utilities for Rhubarb framework."""

import logging
from typing import Any, Dict, Optional
from functools import wraps
from botocore.exceptions import ClientError, BotoCoreError

from .exceptions import (
    DocumentProcessingError,
    VideoProcessingError,
    ModelInvocationError,
    S3AccessError,
    FileFormatError,
    ValidationError
)

logger = logging.getLogger(__name__)


def handle_aws_errors(func):
    """Decorator to handle AWS-specific errors."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code in ['NoSuchBucket', 'NoSuchKey', 'AccessDenied']:
                raise S3AccessError(
                    f"S3 access error: {error_message}",
                    error_code=error_code
                )
            elif error_code in ['ValidationException', 'ThrottlingException']:
                raise ModelInvocationError(
                    f"Bedrock model error: {error_message}",
                    error_code=error_code
                )
            else:
                raise ModelInvocationError(
                    f"AWS service error: {error_message}",
                    error_code=error_code
                )
        except BotoCoreError as e:
            raise ModelInvocationError(f"AWS connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise
    
    return wrapper


def validate_file_path(file_path: str, supported_formats: list = None) -> None:
    """Validate file path and format."""
    if not file_path or not file_path.strip():
        raise ValidationError("File path cannot be empty", parameter="file_path")
    
    if supported_formats:
        file_extension = file_path.lower().split('.')[-1]
        if f".{file_extension}" not in supported_formats:
            raise FileFormatError(
                f"Unsupported file format: .{file_extension}",
                file_path=file_path,
                supported_formats=supported_formats
            )


def validate_parameters(**params) -> None:
    """Validate common parameters."""
    for param_name, param_value in params.items():
        if param_name == "temperature" and param_value is not None:
            if not 0 <= param_value <= 1:
                raise ValidationError(
                    "Temperature must be between 0 and 1",
                    parameter="temperature",
                    value=param_value
                )
        
        elif param_name == "max_tokens" and param_value is not None:
            if param_value <= 0 or param_value > 4096:
                raise ValidationError(
                    "max_tokens must be between 1 and 4096",
                    parameter="max_tokens",
                    value=param_value
                )
        
        elif param_name == "sliding_window_overlap" and param_value is not None:
            if param_value < 0 or param_value > 10:
                raise ValidationError(
                    "sliding_window_overlap must be between 0 and 10",
                    parameter="sliding_window_overlap",
                    value=param_value
                )


def log_error_context(error: Exception, context: Dict[str, Any]) -> None:
    """Log error with context information."""
    logger.error(
        f"Error occurred: {type(error).__name__}: {str(error)}",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
    )


def create_error_response(error: Exception, request_id: Optional[str] = None) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        "error": True,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "request_id": request_id,
        "details": getattr(error, '__dict__', {})
    }
