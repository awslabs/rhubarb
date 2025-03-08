Using Converse API
==================

The Converse API provides streaming capabilities for real-time interactions with documents. This guide demonstrates how to use the Converse API with Rhubarb.

Basic Usage
----------

Here's a simple example of how to use the Converse API:

.. code-block:: python
   :emphasize-lines: 11

    from rhubarb import DocAnalysis, SystemPrompts
    import boto3

    # Initialize a boto3 session
    session = boto3.Session()

    # Create a DocAnalysis instance with converse API
    da = DocAnalysis(
        file_path="./test_docs/employee_enrollment.pdf",
        boto3_session=session,
        use_converse_api=True,
        system_prompt=SystemPrompts().SummarySysPrompt
    )

    # Stream the response
    for resp in da.run_stream(message="Give me a brief summary of this document."):
        if isinstance(resp, str):
            print(resp, end='')
        else:
            print("\n")
            print(resp)


Key Components
-------------

DocAnalysis Parameters
~~~~~~~~~~~~~~~~~~~~~

- ``file_path``: Path to the document you want to analyze
- ``boto3_session``: AWS boto3 session for API authentication
- ``use_converse_api``: Boolean flag to enable streaming responses (default: False)
- ``system_prompt``: System prompt to guide the analysis

Streaming Responses
~~~~~~~~~~~~~~~~~

The ``run_stream()`` method yields responses in real-time. The response can be either:

- A string containing part of the generated text
- A dictionary containing metadata or completion information

Configuration Options
-------------------

System Prompts
~~~~~~~~~~~~~

You can customize the behavior using different system prompts:

.. code-block:: python

    # Using custom system prompt
    custom_prompt = "Analyze this document and provide key insights."
    da = DocAnalysis(
        file_path="document.pdf",
        boto3_session=session,
        use_converse_api=True,
        system_prompt=custom_prompt
    )

    # Using built-in system prompts
    da = DocAnalysis(
        file_path="document.pdf",
        boto3_session=session,
        use_converse_api=True,
        system_prompt=SystemPrompts().SummarySysPrompt
    )
