Document Q&A
============

You can perform question/answering with Rhubarb with as little as 5 lines of code. This is the most basic usage of Rhubarb.

With local file
---------------

Initiaize :code:`DocAnalysis` with a local file and :code:`bedrock` boto3 client and call the :code:`run()` method to get response back. 
In it's default form, it uses a default system prompt.

.. code:: python   

    from rhubarb import DocAnalysis
    import boto3

    session = boto3.Session()
    da = DocAnalysis(file_path="./test_docs/employee_enrollment.pdf", 
                     boto3_session=session)
    resp = da.run(message="What is the employee's name?")

Sample response

.. code-block:: json

   {
     "output": [{
                  "page": 1,
                  "detected_languages": ["English"],
                  "content": "Martha C Rivera"
               }],
     "token_usage": {"input_tokens": 5075, "output_tokens": 51}
   }



With an S3 file
---------------

Initiaize :code:`DocAnalysis` with a file in S3, and boto3 session and call the :code:`run` method to get response back. 
In it's default form, it uses a default system prompt.

.. code:: python
   :emphasize-lines: 5

     from rhubarb import DocAnalysis
     import boto3

     session = boto3.Session()
     da = DocAnalysis(file_path="s3://your-bucket/prefix/document.pdf", 
                      boto3_session=session)
     resp = da.run(message="What is the employee's name?")

