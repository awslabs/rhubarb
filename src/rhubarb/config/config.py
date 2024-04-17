# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from pydantic import Field, BaseModel


class GlobalConfig(BaseModel):
    """
    A class representing global configuration settings.

    Attributes:
        max_retries (int): Maximum number of retries for API calls.
        initial_backoff (float): Initial backoff interval for retries, in seconds.
    """

    max_retries: int = Field(
        default=5, gt=0, description="Maximum number of retries for API calls"
    )
    initial_backoff: float = Field(
        default=1.0,
        gt=0,
        description="Initial backoff interval for retries, in seconds",
    )
    retry_for_incomplete_json: int = Field(
        default=2,
        gt=0,
        description="Number of times the model is re-prompted in case it generates incomplete/invalid JSON",
    )
    classification_prefix: str = Field(
        default="rb_classification", description="Default Classification S3 prefix"
    )
    
    @classmethod
    def update_config(cls, **kwargs):
        """
        Updates the global configuration with the provided values.

        This method creates a new instance of GlobalConfig with the updated values
        and replaces the class-level instance.

        Args:
            **kwargs: Arbitrary keyword arguments corresponding to the GlobalConfig attributes.
        """
        cls._instance = cls(**kwargs)

    @classmethod
    def get_instance(cls):
        """
        Retrieves the current instance of the GlobalConfig.

        If the instance does not exist yet, this method creates a new one with default values.

        Returns:
            GlobalConfig: The current (or newly created) instance of GlobalConfig.
        """
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance
