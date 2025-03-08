Using Cross-Region Inference
===========================

When running model inference in on-demand mode, your requests might be restricted by service quotas or during peak usage times. Cross-region inference enables you to seamlessly manage unplanned traffic bursts by utilizing compute across different AWS Regions. With cross-region inference, you can distribute traffic across multiple AWS Regions, enabling higher throughput.

Basic Usage
----------

Here's a basic example of how to enable Cross-Region Inference:

.. code-block:: python
   :emphasize-lines: 11

    from rhubarb import DocAnalysis, SystemPrompts
    import boto3

    # Initialize a boto3 session
    session = boto3.Session()

    # Create a DocAnalysis instance with cross-region inference
    da = DocAnalysis(
        file_path="./test_docs/employee_enrollment.pdf",
        boto3_session=session,
        enable_cri=True,  # Enable cross-region inference
        system_prompt=SystemPrompts().SummarySysPrompt
    )

    # Run document analysis
    resp = da.run(message="Give me a brief summary of this document.")
    print(resp)


Configuration Options
-------------------

DocAnalysis Parameters
~~~~~~~~~~~~~~~~~~~~~

- ``file_path``: Path to the document for analysis
- ``boto3_session``: AWS boto3 session for authentication
- ``enable_cri``: Boolean flag to enable cross-region inference (default: False)
- ``system_prompt``: System prompt to guide the analysis
- ``target_region``: (Optional) Specify a target AWS region for inference