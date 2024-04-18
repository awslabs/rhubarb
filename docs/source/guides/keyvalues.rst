Key-Values Extraction
=====================

Rhubarb supports extraction of key values using `JSON Schema <https://json-schema.org/learn/getting-started-step-by-step>`_. You 
can pass in a valid JSON schema to extract specific data out of your document.


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
