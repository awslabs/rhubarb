Global Configuration
====================

The ``GlobalConfig`` class is a Pydantic model designed to handle global configuration settings for Rhubarb. It provides a 
structured way to define and access configuration parameters with validation.

Class Definition
----------------

.. code-block:: python

    from pydantic import BaseModel, Field

    class GlobalConfig(BaseModel):
        """
        A class representing global configuration settings.
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

Available Configurations
------------------------

max_retries
^^^^^^^^^^^

- **Type**: ``int``
- **Default**: ``5``
- **Constraints**: Must be greater than 0.
- **Description**: Specifies the maximum number of retries for Amazon Bedrock API calls in case of failures. This setting limits the number of retry attempts after an initial failure to prevent infinite loops and manage throttling.

initial_backoff
^^^^^^^^^^^^^^^

- **Type**: ``float``
- **Default**: ``1.0``
- **Constraints**: Must be greater than 0.
- **Description**: Sets the initial delay in seconds before the first retry following a failed API call. This delay helps manage transient issues that may resolve quickly by providing a brief period before retrying.

retry_for_incomplete_json
^^^^^^^^^^^^^^^^^^^^^^^^^

- **Type**: ``int``
- **Default**: ``2``
- **Constraints**: Must be greater than 0.
- **Description**: The number of attempts to re-prompt the model in case it generates incomplete or invalid JSON. This attribute ensures data integrity by allowing multiple attempts to correct potential data format errors.

classification_prefix
^^^^^^^^^^^^^^^^^^^^^

- **Type**: ``str``
- **Default**: ``"rb_classification"``
- **Description**: Defines the default S3 prefix used to store the document classifier.


Methods
-------

**update_config**

This class method updates the configuration settings for the entire application using Rhubarb. It accepts keyword arguments which correspond to the attributes of the `GlobalConfig` class. 
You can override, one or all configurations to fit your need.

Usage:

.. code-block:: python

    from rhubarb import DocAnalysis, DocClassification, GlobalConfig

    GlobalConfig.update_config(max_retries=10, initial_backoff=2.0)
    # use DocAnalysis() and or DocClassification()

.. note:: 

    You must perform the configuration override before initializing the ``DocClassification`` or ``DocAnalysis`` class in your code.

See also:
^^^^^^^^^
.. seealso:: For broader context, see :doc:`../introduction`.