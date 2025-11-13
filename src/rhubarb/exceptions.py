# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Custom exceptions for Rhubarb framework."""


class RhubarbError(Exception):
    """Base exception for all Rhubarb errors."""
    pass


class DocumentProcessingError(RhubarbError):
    """Raised when document processing fails."""
    
    def __init__(self, message: str, file_path: str = None, error_code: str = None):
        self.file_path = file_path
        self.error_code = error_code
        super().__init__(message)


class VideoProcessingError(RhubarbError):
    """Raised when video processing fails."""
    
    def __init__(self, message: str, file_path: str = None, error_code: str = None):
        self.file_path = file_path
        self.error_code = error_code
        super().__init__(message)


class ClassificationError(RhubarbError):
    """Raised when document classification fails."""
    
    def __init__(self, message: str, samples: list = None, error_code: str = None):
        self.samples = samples
        self.error_code = error_code
        super().__init__(message)


class ModelInvocationError(RhubarbError):
    """Raised when AWS Bedrock model invocation fails."""
    
    def __init__(self, message: str, model_id: str = None, error_code: str = None):
        self.model_id = model_id
        self.error_code = error_code
        super().__init__(message)


class FileFormatError(RhubarbError):
    """Raised when file format is not supported."""
    
    def __init__(self, message: str, file_path: str = None, supported_formats: list = None):
        self.file_path = file_path
        self.supported_formats = supported_formats
        super().__init__(message)


class S3AccessError(RhubarbError):
    """Raised when S3 access fails."""
    
    def __init__(self, message: str, bucket: str = None, key: str = None, error_code: str = None):
        self.bucket = bucket
        self.key = key
        self.error_code = error_code
        super().__init__(message)


class ValidationError(RhubarbError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, parameter: str = None, value=None):
        self.parameter = parameter
        self.value = value
        super().__init__(message)


class ConfigurationError(RhubarbError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: str = None, config_value=None):
        self.config_key = config_key
        self.config_value = config_value
        super().__init__(message)
