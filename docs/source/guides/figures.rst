Working with images
===================

Rhubarb can also help perform explanation and reasoning on images, charts, graphs within documents. The :code:`FigureSysPrompt` 
exclusively handles images within documents.

.. code:: python
   :emphasize-lines: 5

    from rhubarb import DocAnalysis, SystemPrompts

    da = DocAnalysis(file_path="./test_docs/scientific_paper.pdf", 
                    boto3_session=session,
                    system_prompt=SystemPrompts().FigureSysPrompt)
    resp = da.run(message="Explain the bar chart in this document.")

Sample output

.. code-block:: json

    {
        "output": [
            {
                "page": 1,
                "figure_analysis": "The bar chart shows the normalized purchases of the same type of product, as a function of the number of days from the request, in late shopping stages. The y-axis represents the normalized number of purchases, and the x-axis represents the days after the request, from 0 to 15 days. The chart has three bars for each day, representing purchases of the 'Same Product', 'Same Type', and 'Unrelated Purchases'.",
                "figure_description": "Figure 2: Normalized purchases of the same type, as function of the days from the request, in late shopping stages.",
                "reasoning": "The chart is titled 'Figure 2: Normalized purchases of the same type, as function of the days from the request, in late shopping stages.' The y-axis is labeled 'Normalized number of purchases' and the x-axis is labeled 'Days after the request'. There are three bars for each day from 0 to 15, representing the normalized purchases of the 'Same Product', 'Same Type', and 'Unrelated Purchases'. This allows for a comparison of purchase behavior across these categories over time after the initial request."
            }
        ],
        "token_usage": {
            "input_tokens": 1861,
            "output_tokens": 288
        }
    }


Reasoning with tables (experimental)
------------------------------------

We can also perform reasoning with tables using the Figure System Prompt.

.. code:: python

    from rhubarb import DocAnalysis, SystemPrompts

    da = DocAnalysis(file_path="./test_docs/amzn-10k.pdf", 
                    boto3_session=session,
                    system_prompt=SystemPrompts().FigureSysPrompt)
    resp = da.run(message="What is the dollar value difference of Net Sales between 2022 and 2023 for North America in the given table. Explain your answer.")

Sample output

.. code-block:: json

    {
        "output": [
            {
                "page": 1,
                "figure_analysis": "The Net Sales for North America increased from $315,880 million in 2022 to $352,828 million in 2023, a difference of $36,948 million.",
                "figure_description": "A table showing Net Sales broken down by segment (North America, International, AWS) for the years ended December 31, 2022 and 2023.",
                "reasoning": "In the 'Net Sales' table on page 1, the value for 'North America' in the 2022 column is $315,880 million. The value for 'North America' in the 2023 column is $352,828 million. The difference between these two values is $352,828 million - $315,880 million = $36,948 million."
            }
        ],
        "token_usage": {
            "input_tokens": 4960,
            "output_tokens": 209
        }
    }
