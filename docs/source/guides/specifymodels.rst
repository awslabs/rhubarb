Change Default Model
====================

By default Rhubarb uses Claude Sonnet model, however you can also use Haiku, Opus, Nova Pro, or Nova Lite. Different Language Models are available via 
:code:`LanguageModel` class.

- :code:`LanguageModel.CLAUDE_HAIKU_V1`
- :code:`LanguageModel.CLAUDE_SONNET_V1`
- :code:`LanguageModel.CLAUDE_SONNET_V2` (default)
- :code:`LanguageModel.CLAUDE_SONNET_4`
- :code:`LanguageModel.CLAUDE_OPUS_4`
- :code:`LanguageModel.CLAUDE_OPUS_V1`
- :code:`LanguageModel.NOVA_PRO`
- :code:`LanguageModel.NOVA_LITE`

Use Claude Haiku -

.. code:: python
   :emphasize-lines: 5

     from rhubarb import DocAnalysis, LanguageModels

     da = DocAnalysis(file_path="s3://your-bucket/employee_enrollment.pdf", 
                      boto3_session=session,
                      modelId=LanguageModels.CLAUDE_HAIKU_V1)
     resp = da.run(message="What is the employee's name?")

Or Claude Opus -

.. code:: python
   :emphasize-lines: 5
   
     from rhubarb import DocAnalysis, LanguageModels

     da = DocAnalysis(file_path="s3://your-bucket/employee_enrollment.pdf", 
                      boto3_session=session,
                      modelId=LanguageModels.CLAUDE_OPUS_V1)
     resp = da.run(message="What is the employee's name?")

Or Nova Pro - 

.. code:: python
   :emphasize-lines: 5
   
     from rhubarb import DocAnalysis, LanguageModels

     da = DocAnalysis(file_path="s3://your-bucket/employee_enrollment.pdf", 
                      boto3_session=session,
                      modelId=LanguageModels.NOVA_PRO)
     resp = da.run(message="What is the employee's name?")