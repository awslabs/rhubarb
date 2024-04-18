Schema Creation Assistant
=========================

Rhubarb can also help create accurate JSON schemas from plain text prompts. You can provide a document and ask it to extract 
certain values from the document and it will respond back with a JSON schema. You can then use the JSON schema with the 
:code:`output_schema` as shown above, or you can tweak and modify it to fit your need further. You do this using the 
:code:`generate_schema()` function.

.. code:: python

    from rhubarb import DocAnalysis

    da = DocAnalysis(file_path="./test_docs/employee_enrollment.pdf", 
                    boto3_session=session,
                    pages=[1])
    resp = da.generate_schema(message="I want to extract the employee name, employee SSN, employee address, \
                                       date of birth and phone number from this document.")
    resp['output']

Sample output

.. code-block:: json

    {
      "type": "object",
      "properties": {
        "employeeName": {
          "type": "object",
          "properties": {
            "first": {
              "type": "string",
              "description": "The employee's first name"
            },
            "initial": {
              "type": "string",
              "description": "The employee's middle initial"
            },
            "last": {
              "type": "string",
              "description": "The employee's last name"
            }
          },
          "required": ["first", "last"]
        },
        "employeeSSN": {
          "type": "string",
          "description": "The employee's social security number"
        },
        "employeeAddress": {
          "type": "object",
          "properties": {
            "street": {
              "type": "string",
              "description": "The employee's street address"
            },
            "city": {
              "type": "string",
              "description": "The employee's city"
            },
            "state": {
              "type": "string",
              "description": "The employee's state"
            },
            "zipCode": {
              "type": "string",
              "description": "The employee's zip code"
            }
          },
          "required": ["street", "city", "state", "zipCode"]
        },
        "dateOfBirth": {
          "type": "string",
          "description": "The employee's date of birth in MM/DD/YY format"
        },
        "phoneNumber": {
          "type": "string",
          "description": "The employee's phone number"
        }
      },
      "required": [
        "employeeName",
        "employeeSSN",
        "employeeAddress",
        "dateOfBirth",
        "phoneNumber"
      ]
    }


We can then use this schema to perform extraction on the same document.

.. code:: python

    output_schema = resp['output']
    resp = da.run(message="I want to extract the employee name, employee SSN, employee address, date of \
                           birth and phone number from this document. Use the schema provided.", 
                  output_schema=output_schema)

Sample output

.. code-block:: json

    {
      "output": {
        "employeeName": {
          "first": "Martha",
          "initial": "C",
          "last": "Rivera"
        },
        "employeeSSN": "376 12 1987",
        "employeeAddress": {
          "street": "8 Any Plaza, 21 Street",
          "city": "Any City",
          "state": "CA",
          "zipCode": "90210"
        },
        "dateOfBirth": "09/19/80",
        "phoneNumber": "(383) 555-0100"
      },
      "token_usage": {
        "input_tokens": 2107,
        "output_tokens": 146
      }
    }

Schema creation assistance with question rephrase
-------------------------------------------------

In many cases you may want to quickly get started with creating a JSON Schema for your document wihtout spending too much 
time crafting a proper prompt for the document. For example, in a birth certificate you could be vague in asking a question 
such as "*I want to get the child's, the mother's and father's details from the given document*". In such cases Rhubarb can 
help rephrasing the question and create an appropriate rephrased question based on the document and generate a subsequent 
schema for it which can directly be used to extract the data. For this, you use the :code:`assistive_rephrase` parameter in your call 
to :code:`generate_schema()` function.

.. code:: python
   :emphasize-lines: 5,6

    from rhubarb import DocAnalysis

    da = DocAnalysis(file_path="./test_docs/birth_cert.jpeg",
                     boto3_session=session)
    resp = da.generate_schema(message="I want to get the child's, the mother's and father's details from the given document",
                              assistive_rephrase=True)
    resp['output']

Sample output

.. code-block:: json

    {
      "rephrased_question": "Extract the child's name, date of birth, sex, place of birth, mother's name, mother's date of birth, mother's place of birth, mother's address, father's name, and father's place of birth from the given birth certificate document.",
      "output_schema": {
        "type": "object",
        "properties": {
          "child": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string",
                "description": "The child's full name"
              },
              "dateOfBirth": {
                "type": "string",
                "description": "The child's date of birth"
              },
              "sex": {
                "type": "string",
                "description": "The child's sex"
              },
              "placeOfBirth": {
                "type": "string",
                "description": "The child's place of birth"
              }
            },
            "required": ["name", "dateOfBirth", "sex", "placeOfBirth"]
          },
          "mother": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string",
                "description": "The mother's full name"
              },
              "dateOfBirth": {
                "type": "string",
                "description": "The mother's date of birth"
              },
              "placeOfBirth": {
                "type": "string",
                "description": "The mother's place of birth"
              },
              "address": {
                "type": "string",
                "description": "The mother's address"
              }
            },
            "required": ["name", "dateOfBirth", "placeOfBirth", "address"]
          },
          "father": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string",
                "description": "The father's full name"
              },
              "placeOfBirth": {
                "type": "string",
                "description": "The father's place of birth"
              }
            },
            "required": ["name", "placeOfBirth"]
          }
        },
        "required": ["child", "mother", "father"]
      }
    }

And then use the rephrased question and the :code:`output_schema`.

.. code:: python
   :emphasize-lines: 1,2

    output_schema = resp['output']['output_schema']
    question = resp['output']['rephrased_question']

    resp = da.run(message = question,
                  output_schema = output_schema)