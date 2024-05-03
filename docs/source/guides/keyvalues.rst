Structured Data Extraction
=====================

Rhubarb supports extraction of key values using JSON Schemas. You can pass in a valid JSON schema to extract specific data out of your document.

.. note:: JSON Schema is a declarative language that you can use to annotate and validate the structure, constraints, and data types of your JSON documents. It provides a way to standardize and define expectations for your JSON data. `Learn more <https://json-schema.org/learn/getting-started-step-by-step>`_.


.. code:: python

    schema = {
        "type": "object",
        "properties": {
            "employee_name": {
                "description": "Employee's Name",
                "type": "string"
            },
            "employee_ssn": {
                "description": "Employee's social security number",
                "type": "string"
            },
            "employee_address": {
                "description": "Employee's mailing address",
                "type": "string"
            },
            "employee_dob": {
                "description": "Employee's date of birth",
                "type": "string"
            },
            "employee_gender": {
                "description": "Employee's gender",
                "type": "object",
                "properties": {
                    "male":{
                        "description": "Whether the employee gender is Male",
                        "type": "boolean"
                    },
                    "female":{
                        "description": "Whether the employee gender is Female",
                        "type": "boolean"
                    }
                },
                "required": ["male", "female"]
            },
            "employee_hire_date": {
                "description": "Employee's hire date",
                "type": "string"
            },
            "employer_no": {
                "description": "Employer number",
                "type": "string"
            },
            "employment_status": {
                "type": "object",
                "description": "Employment status",
                "properties": {
                    "full_time":{
                        "description": "Whether employee is full-time",
                        "type": "boolean"
                    },
                    "part_time": {
                        "description": "Whether employee is part-time",
                        "type": "boolean"
                    }
                },
                "required": ["full_time", "part_time"]
            },
            "employee_salary_rate":{
                "description": "The dollar value of employee's salary",
                "type": "integer"
            },
            "employee_salary_frequency":{
                "type": "object",
                "description": "Salary rate of the employee",
                "properties": {
                    "annual":{
                        "description": "Whether salary rate is monthly",
                        "type": "boolean"
                    },
                    "monthly": {
                        "description": "Whether salary rate is monthly",
                        "type": "boolean"
                    },
                    "semi_monthly": {
                        "description": "Whether salary rate is semi_monthly",
                        "type": "boolean"
                    },
                    "bi_weekly": {
                        "description": "Whether salary rate is bi_weekly",
                        "type": "boolean"
                    },
                    "weekly": {
                        "description": "Whether salary rate is weekly",
                        "type": "boolean"
                    }
                },
                "required": ["annual", "monthly", "semi_monthly","bi_weekly","weekly"]
            }
        },
        "required": ["employee_name","employee_hire_date", "employer_no", "employment_status"]
    }

The pass the JSON Schema to :code:`DocAnalysis` to perform extraction

.. code:: python
   :emphasize-lines: 6

    from rhubarb import DocAnalysis

    da = DocAnalysis(file_path="./test_docs/employee_enrollment.pdf", 
                    boto3_session=session)
    resp = da.run(message="Give me the output based on the provided schema.", 
                  output_schema=schema)

Sample output conforming to the custom JSON Schema

.. code-block:: json

    {
        "output": {
            "employee_name": "Martha C Rivera",
            "employee_ssn": "376 12 1987",
            "employee_address": "8 Any Plaza, 21 Street Any City CA 90210",
            "employee_dob": "09/19/80",
            "employee_gender": {
                "male": false,
                "female": true
            },
            "employee_hire_date": "07/19/2023",
            "employer_no": "784371",
            "employment_status": {
                "full_time": true,
                "part_time": false
            },
            "employee_salary_rate": 79930,
            "employee_salary_frequency": {
                "annual": true,
                "monthly": false,
                "semi_monthly": false,
                "bi_weekly": false,
                "weekly": false
            }
        },
        "token_usage": {
            "input_tokens": 5379,
            "output_tokens": 222
        }
    }

Auto Schemas
------------

Rhubarb can also help create accurate JSON schemas from plain text prompts. You can provide a document and ask it to extract 
certain values from the document and it will respond back with a JSON schema. You can then use the JSON schema with the 
:code:`output_schema` as shown above, or you can tweak and modify it to fit your need further. You do this using the 
:code:`generate_schema()` function.

.. code:: python

    from rhubarb import DocAnalysis

    da = DocAnalysis(file_path="./test_docs/employee_enrollment.pdf", 
                    boto3_session=session,
                    pages=[1])
    prompt="I want to extract the employee name, employee SSN, employee address, \
            date of birth and phone number from this document."
    resp = da.generate_schema(message=prompt)        
    response = da.run(message=prompt, 
                      output_schema=resp['output'])


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

Auto schema with question rephrase
----------------------------------

In many cases you may want to quickly get started with creating a JSON Schema for your document wihtout spending too much 
time crafting a proper prompt for the document. For example, in a birth certificate you could be vague in asking a question 
such as "*the child's, the mother's and father's details from the given document*". In such cases Rhubarb can 
help rephrasing the question and create an appropriate rephrased question based on the document and generate a subsequent 
schema for it which can directly be used to extract the data. For this, you use the :code:`assistive_rephrase` parameter in your call 
to :code:`generate_schema()` function.

.. code:: python
   :emphasize-lines: 5,6

    from rhubarb import DocAnalysis

    da = DocAnalysis(file_path="./test_docs/birth_cert.jpeg",
                     boto3_session=session)
    resp = da.generate_schema(message="the child's, the mother's and father's details from the given document",
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


Tables Extraction (experimental)
--------------------------------

You can also perform table extraction using custom JSON schema. In this case we will use a rather complex table from an 
AMZN 10-k filing document and attempt to extract the data from it. Here's what a JSON schema might look like.

.. code:: python

    table_schema = {
        "additionalProperties": {
            "type": "object",
            "patternProperties": {
            "^(2022|2023)$": {
                "type": "object",
                "properties": {
                "Net Sales": {
                    "type": "object",
                    "properties": {
                    "North America": {
                        "type": "number"
                    },
                    "International": {
                        "type": "number"
                    },
                    "AWS": {
                        "type": "number"
                    },
                    "Consolidated": {
                        "type": "number"
                    }
                    },
                    "required": ["North America", "International", "AWS", "Consolidated"]
                },
                "Year-over-year Percentage Growth (Decline)": {
                    "type": "object",
                    "properties": {
                    "North America": {
                        "type": "number"
                    },
                    "International": {
                        "type": "number"
                    },
                    "AWS": {
                        "type": "number"
                    },
                    "Consolidated": {
                        "type": "number"
                    }
                    },
                    "required": ["North America", "International", "AWS", "Consolidated"]
                },
                "Year-over-year Percentage Growth, excluding the effect of foreign exchange rates": {
                    "type": "object",
                    "properties": {
                    "North America": {
                        "type": "number"
                    },
                    "International": {
                        "type": "number"
                    },
                    "AWS": {
                        "type": "number"
                    },
                    "Consolidated": {
                        "type": "number"
                    }
                    },
                    "required": ["North America", "International", "AWS", "Consolidated"]
                },
                "Net Sales Mix": {
                    "type": "object",
                    "properties": {
                    "North America": {
                        "type": "number"
                    },
                    "International": {
                        "type": "number"
                    },
                    "AWS": {
                        "type": "number"
                    },
                    "Consolidated": {
                        "type": "number"
                    }
                    },
                    "required": ["North America", "International", "AWS", "Consolidated"]
                }
                },
                "required": ["Net Sales", "Year-over-year Percentage Growth (Decline)", "Year-over-year Percentage Growth, excluding the effect of foreign exchange rates", "Net Sales Mix"]
            }
            }
        }
    }

We are only interested in the results of operation which we know is in the first page, we will call Rhubarb with just the first page in this case to save costs. However, in situations where the 
table's exact location isn't known, the full document can be passed.

.. code:: python

    from rhubarb import DocAnalysis

    da = DocAnalysis(file_path="./test_docs/amzn-10k.pdf", 
                    boto3_session=session,
                    pages=[1])
    resp = da.run(message="Give me data in the results of operation table from this 10-K SEC filing document. Use the schema provided.", 
                  output_schema=table_schema)
    resp

Sample output in table table schema

.. code-block:: json

    {
        "output": {
            "2022": {
                "Net Sales": {
                    "North America": 315880,
                    "International": 118007,
                    "AWS": 80096,
                    "Consolidated": 513983
                },
                "Year-over-year Percentage Growth (Decline)": {
                    "North America": 13,
                    "International": -8,
                    "AWS": 29,
                    "Consolidated": 9
                },
                "Year-over-year Percentage Growth, excluding the effect of foreign exchange rates": {
                    "North America": 13,
                    "International": 4,
                    "AWS": 29,
                    "Consolidated": 13
                },
                "Net Sales Mix": {
                    "North America": 61,
                    "International": 23,
                    "AWS": 16,
                    "Consolidated": 100
                }
            },
            "2023": {
                "Net Sales": {
                    "North America": 352828,
                    "International": 131200,
                    "AWS": 90757,
                    "Consolidated": 574785
                },
                "Year-over-year Percentage Growth (Decline)": {
                    "North America": 12,
                    "International": 11,
                    "AWS": 13,
                    "Consolidated": 12
                },
                "Year-over-year Percentage Growth, excluding the effect of foreign exchange rates": {
                    "North America": 12,
                    "International": 11,
                    "AWS": 13,
                    "Consolidated": 12
                },
                "Net Sales Mix": {
                    "North America": 61,
                    "International": 23,
                    "AWS": 16,
                    "Consolidated": 100
                }
            }
        },
        "token_usage": {
            "input_tokens": 2181,
            "output_tokens": 433
        }
    }
