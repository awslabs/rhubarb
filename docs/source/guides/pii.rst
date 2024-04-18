PII Recognition
===============

Just like :doc:`ner`, you can also perform PII (Personally Identifiable Information) detection. Infact, the default NER entities,
is just a super-set of PII entities. For example, :code:`Entities.NAME` and :code:`Entities.SSN` are PII entities.

.. code:: python
   :emphasize-lines: 7

     from rhubarb import DocAnalysis, Entities

     da = DocAnalysis(file_path="./test_docs/employee_enrollment.pdf", 
                    boto3_session=session,
                    pages=[1,3])
     resp = da.run_entity(message="Extract all the specified entities from this document.", 
                          entities=[Entities.ADDRESS, Entities.SSN])

Sample output

.. code-block:: json

    {
        "output": [
            {
                "page": 1,
                "entities": [
                    {"SSN": "376 12 1987"},
                    {"ADDRESS": "8 Any Plaza, 21 Street"}
                ]
            },
            {
                "page": 3,
                "entities": [
                    {"SSN": "791 36 9771"},
                    {"ADDRESS": "8 Any Plaza, 21 Street"},
                    {"SSN": "824 26 2211"},
                    {"ADDRESS": "8 Any Plaza, 21 Street"}
                ]
            }
        ],
        "token_usage": {
            "input_tokens": 3534,
            "output_tokens": 183
        }
    }
