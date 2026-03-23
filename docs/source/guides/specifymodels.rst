Change Default Model
====================

By default Rhubarb uses Claude Sonnet 4.6 model. Different Language Models are available via
:code:`LanguageModels` class.

**Anthropic Claude Models:**

- :code:`LanguageModels.CLAUDE_SONNET_4_6` (default)
- :code:`LanguageModels.CLAUDE_HAIKU_4_5`
- :code:`LanguageModels.CLAUDE_OPUS_4_6`

**Amazon Nova Models:**

- :code:`LanguageModels.NOVA_PRO`
- :code:`LanguageModels.NOVA_LITE`
- :code:`LanguageModels.NOVA_2_LITE`

Use Claude Haiku -

.. code:: python
   :emphasize-lines: 5

     from rhubarb import DocAnalysis, LanguageModels

     da = DocAnalysis(file_path="s3://your-bucket/employee_enrollment.pdf",
                      boto3_session=session,
                      modelId=LanguageModels.CLAUDE_HAIKU_4_5)
     resp = da.run(message="What is the employee's name?")

Or Claude Opus -

.. code:: python
   :emphasize-lines: 5

     from rhubarb import DocAnalysis, LanguageModels

     da = DocAnalysis(file_path="s3://your-bucket/employee_enrollment.pdf",
                      boto3_session=session,
                      modelId=LanguageModels.CLAUDE_OPUS_4_6)
     resp = da.run(message="What is the employee's name?")

Or Amazon Nova 2 Lite -

.. code:: python
   :emphasize-lines: 5

     from rhubarb import DocAnalysis, LanguageModels

     da = DocAnalysis(file_path="s3://your-bucket/employee_enrollment.pdf",
                      boto3_session=session,
                      modelId=LanguageModels.NOVA_2_LITE)
     resp = da.run(message="What is the employee's name?")

Or Nova Pro -

.. code:: python
   :emphasize-lines: 5

     from rhubarb import DocAnalysis, LanguageModels

     da = DocAnalysis(file_path="s3://your-bucket/employee_enrollment.pdf",
                      boto3_session=session,
                      modelId=LanguageModels.NOVA_PRO)
     resp = da.run(message="What is the employee's name?")


Native PDF Support
==================

Claude models support native PDF processing, sending PDFs directly as document blocks instead of converting pages to images.
This supports up to **600 pages** per request and provides better text extraction alongside visual understanding.

Native PDF support is automatic — when you pass a PDF file with a Claude model, Rhubarb uses the native path. No code changes needed.

.. note:: Native PDF support is only available for Claude models using the ``invoke_model`` API (not Converse API). Nova models and image files (PNG, JPG, TIFF) continue using image-based conversion.
