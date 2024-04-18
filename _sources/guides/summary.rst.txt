Document Summarization
======================

Rhubarb can generate sumarries of a document. You can generate summary for an entire document (20 pages max), or selective pages.

Page level summaries
--------------------

By default :code:`DocAnalysis` generates page level summaries.

.. code:: python

    from rhubarb import DocAnalysis

    da = DocAnalysis(file_path="./test_docs/employee_enrollment.pdf", 
                     boto3_session=session)
    resp = da.run(message="Give me a brief summary for each page.")
    resp

Sample output

.. code-block:: json

    {
      "output": [
        {
          "page": 1,
          "detected_languages": ["English"],
          "content": "This page contains an employee enrollment form for 401(k) plans with designated Roth contributions. It includes fields for the employer's name, employee's personal information, salary details, contribution percentages, and effective dates."
        },
        {
          "page": 2,
          "detected_languages": ["English"],
          "content": "This page outlines the allocation of contributions across various investment funds offered by the company, including interest accumulation accounts, equity funds, real estate funds, retirement funds, balanced funds, asset allocation funds, and fixed income funds."
        },
        {
          "page": 3,
          "detected_languages": ["English"],
          "content": "This page allows the employee to designate primary and secondary beneficiaries for their retirement account. It includes fields for beneficiary information such as name, relationship, address, and benefit percentage. It also contains a spouse's waiver section and the employee's signature confirming participation in the plan."
        }
      ],
      "token_usage": {
        "input_tokens": 5077,
        "output_tokens": 269
      }
    }


Full document summary
---------------------

You can generate an overall summary of the entire document. In this case, we will override the default System Prompt which 
breaks down the response per page. Rhubarb comes with a Summary specific System Prompt for the model, available via 
:code:`SystemPrompts`.

.. code:: python
   :emphasize-lines: 5

    from rhubarb import DocAnalysis, SystemPrompts

    da = DocAnalysis(file_path="./test_docs/employee_enrollment.pdf", 
                     boto3_session=session,
                     system_prompt=SystemPrompts().SummarySysPrompt)
    resp = da.run(message="Give me a brief summary of this document.")

Sample output

.. code-block:: json

    {
        "output": "This document is an Employee Enrollment Form for 401(k) Plans with Designated Roth Contributions from AnyCompany of America Life Insurance Co. It contains the following key information:\\n\\n- Employee details: A female employee named Martha C. Rivera, hired on 07/19/2023 as a full-time employee with an annual salary of $79,930. Her personal information like address, date of birth, and contact details are provided.\\n\\n- Contribution details: The employee is enrolling in the company's 401(k) plan with 10% of salary allocated to Traditional Pre-Tax Contributions effective 08/19/23 and 08/19/23 for employer matching and non-matching contributions respectively. No Designated Roth Contributions are specified.\\n\\n- Investment allocation: 50% of contributions will be placed in the AnyCompany of America Interest Accumulation Account, while the remaining investment options are listed.\\n\\n- Beneficiary designations: The employee has named her spouse as the primary beneficiary with 50% benefit and her child as the secondary beneficiary with 50% benefit. The spouse has signed a waiver allowing this arrangement.\\n\\n- Signature: The employee has signed the form on 3/25/2022, indicating she has reviewed the plan materials and finds it suitable for her financial needs.",
        "token_usage": {
            "input_tokens": 4755, 
            "output_tokens": 292
        }
    }



Specific page(s) summary
------------------------

You can also perform summarization of specific pages using the :code:`pages` parameter.

.. code:: python
   :emphasize-lines: 6

    from rhubarb import DocAnalysis, SystemPrompts

    da = DocAnalysis(file_path="./test_docs/employee_enrollment.pdf", 
                     boto3_session=session,
                     system_prompt=SystemPrompts().SummarySysPrompt,
                     pages=[1,3])
    resp = da.run(message="Give me a brief summary of this document.")

Sample output

.. code-block:: json

    {
        "output": "## Summary\n\nThis document is an employee enrollment form for a 401(k) plan with designated Roth contributions from AnyCompany of America Life Insurance Co. The key details are:\n\n- The employee is Martha C. Rivera, hired on 07/19/2023 as a full-time employee with an annual salary of $79,930. \n- Her employer is AnyCompany Constructions Inc. with the employer number 784371.\n- Traditional pre-tax contributions are set at 10% of salary effective 08/19/23 and employer matching contributions effective 08/19/23.\n- Martha has designated her spouse Mateo Rivera as the primary beneficiary at 50% and her child Pat Rivera as the secondary beneficiary at 50%.\n- Mateo has signed a spouse's waiver allowing Martha to receive the death benefit after his death.\n- Martha has signed the form on 3/25/2022, indicating she has read the plan materials and wishes to participate in the Thrift Plan.",
        "token_usage": {
            "input_tokens": 3207, 
            "output_tokens": 228
        }
    }


Streaming summary
-----------------

In some cases, you may want to stream the summaries for example let's say a real time chat application. You can easily do that 
using the :code:`run_stream()` method. 

.. code:: python
   :emphasize-lines: 7

    from rhubarb import DocAnalysis, SystemPrompts

    da = DocAnalysis(file_path="./test_docs/employee_enrollment.pdf", 
                     boto3_session=session,
                     system_prompt=SystemPrompts().SummarySysPrompt)

    for resp in da.run_stream(message="Give me a brief summary of this document."):
        if isinstance(resp, str):
            print(resp,end='')
        else:
            print("\n")
            print(resp)

Sample output

.. code-block:: text

    |-START-|
    This document is an Employee Enrollment Form for 401(k) Plans with Designated Roth Contributions from AnyCompany of America Life Insurance Co. It contains the following key information:

    - Employee details: A female employee named Martha C. Rivera, hired on 07/19/2023 as a full-time employee with an annual salary of $79,930. Her personal information like address, date of birth, and contact details are provided.

    - Contribution details: The employee is enrolling in the company's 401(k) plan with 10% of salary allocated to Traditional Pre-Tax Contributions effective 08/19/23 and 08/19/23 for employer matching and non-matching contributions respectively. No Designated Roth Contributions are specified.

    - Investment allocation: 50% of contributions will be placed in the AnyCompany of America Interest Accumulation Account, while the remaining options for separate investment funds like equity, real estate, retirement, balanced, asset allocation, and fixed income funds are listed.

    - Beneficiary designations: Martha has designated her spouse (Mateo Rivera) as the primary beneficiary at 50% and her son (Pat Rivera) as the secondary beneficiary at 50%. The spouse has signed a waiver allowing this arrangement.

    - Employee signature: Martha has signed the form on 3/25/2022, indicating she has reviewed the plan materials and finds it suitable for her financial needs.
    |-END-|

    {'input_tokens': 4755, 'output_tokens': 317}

Text streaming starts with a :code:`|-START-|` marker and the end of streaming is marked with an :code:`|-END-|` marker. This is to make sure that the application client recieving the stream has a clear demarcation of when the streaming starts and ends. 
Currently Rhubarb doesn't support :code:`stop_words` kwargs during model invocation but that is coming soon.

One thing to keep in mind is that streaming may only makes sense for a couple of use cases

- One where a lot of text (like summary) is expected from the model and you have a specific need to reduce the time to first token
- A real time conversational chat interface a.k.a. ChatBot

You can also view the chat history by accessing the :code:`history` property.

.. code:: python

    da.history