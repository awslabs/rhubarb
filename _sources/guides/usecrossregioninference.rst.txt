Using Cross-Region Inference
===========================

When running model inference in on-demand mode, your requests might be restricted by service quotas or during peak usage times. Cross-region inference enables you to seamlessly manage unplanned traffic bursts by utilizing compute across different AWS Regions. With cross-region inference, you can distribute traffic across multiple AWS Regions, enabling higher throughput.

Rhubarb supports cross-region inference via the ``cross_region_inference`` parameter:

- ``"us"`` (default): Routes requests within US AWS regions.
- ``"global"``: Routes requests across 20+ AWS regions worldwide. Provides ~10% cost savings and higher throughput.
- ``None``: Disabled, uses the model ID directly.

Basic Usage
----------

Cross-region inference is enabled by default (``"us"``):

.. code-block:: python
   :emphasize-lines: 11

    from rhubarb import DocAnalysis, SystemPrompts
    import boto3

    # Initialize a boto3 session
    session = boto3.Session()

    # Create a DocAnalysis instance (cross-region inference is "us" by default)
    da = DocAnalysis(
        file_path="./test_docs/employee_enrollment.pdf",
        boto3_session=session,
        cross_region_inference="us",
        system_prompt=SystemPrompts().SummarySysPrompt
    )

    # Run document analysis
    resp = da.run(message="Give me a brief summary of this document.")
    print(resp)


Global Cross-Region Inference
----------------------------

Use global cross-region inference for higher throughput and ~10% cost savings:

.. code-block:: python
   :emphasize-lines: 5

    da = DocAnalysis(
        file_path="./test_docs/employee_enrollment.pdf",
        boto3_session=session,
        cross_region_inference="global",
    )
    resp = da.run(message="Give me a brief summary of this document.")

Disable Cross-Region Inference
-----------------------------

.. code-block:: python
   :emphasize-lines: 5

    da = DocAnalysis(
        file_path="./test_docs/employee_enrollment.pdf",
        boto3_session=session,
        cross_region_inference=None,
    )
    resp = da.run(message="Give me a brief summary of this document.")


Configuration Options
-------------------

DocAnalysis Parameters
~~~~~~~~~~~~~~~~~~~~~

- ``file_path``: Path to the document for analysis
- ``boto3_session``: AWS boto3 session for authentication
- ``cross_region_inference``: ``"us"`` (default), ``"global"``, or ``None`` to disable
- ``system_prompt``: System prompt to guide the analysis

.. note:: Not all models support global cross-region inference. Claude Opus 4.6, Sonnet 4.6, Haiku 4.5, and Nova 2 Lite support global profiles. Nova Pro and Nova Lite only support US cross-region profiles. See `AWS documentation <https://docs.aws.amazon.com/bedrock/latest/userguide/global-cross-region-inference.html>`_ for details.
