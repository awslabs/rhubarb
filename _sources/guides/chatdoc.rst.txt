Chat with Documents
===================

You can chat with your documents with Rhubarb using the Chat System Prompt :code:`ChatSysPrompt` available via :code:`SystemPrompts` 
class. Here's an example of a (non-streaming) chat. Note, that internally Rhubarb does support chat history, however, much of 
the history implementation is left to the developer. This coupled with the fact that Claude models only accept 20 images per 
invocation, makes it a little complicated to properly implement chat history based conversational system. We are working on 
simplifying this more, and will add support in upcoming releases.

Also note that there isn't a lot of fundamental difference between the default invocation using Rhubarb vs. invocation using 
the :code:`ChatSysPrompt`. The difference is in the response structure. While default is capable of giving you responses to 
your question on a per page basis, chat gives you the output (i.e. response to your chat) and optionally cites the source 
(i.e. the page number). So in conclusion, the only difference is the response payload structure.

For non streaming chat responses, below is the output structure-

.. code-block:: json
   
    {
        "output": 
        {
            "text": "Response", 
            "sources": [1, 2, 3],  // these are the page numbers
            "quotes": ["quote 1", "quote 2", "quote 3"] // these are the verbatim quotes from the document
        }, 
        "token_usage": 
        {
            "input_tokens": 5029, 
            "output_tokens": 215
        }
    }

.. code:: python
   :emphasize-lines: 5

    from rhubarb import DocAnalysis, SystemPrompts

    da = DocAnalysis(file_path="./test_docs/amzn-10k.pdf", 
                     boto3_session=session,
                     system_prompt=SystemPrompts().ChatSysPrompt)
    resp = da.run(message="What is this document about?")    

Sample output

.. code-block:: json

    {
        "output": {
            "text": "This document appears to be a financial report or annual report for a company, likely Amazon, based on the references to business segments like North America, International, and AWS (Amazon Web Services). It provides details on the company's results of operations, net sales, operating income/loss, operating expenses, cost of sales, and fulfillment costs across these segments for the years 2022 and 2023.",
            "sources": [1, 2, 3],
            "quotes": [
                "We have organized our operations into three segments: North America, International, and AWS. These segments reflect the way the Company evaluates its business performance and manages its operations.",
                "Operating income (loss) by segment is as follows (in millions):",
                "Cost of sales primarily consists of the purchase price of consumer products, inbound and outbound shipping costs, including costs related to sortation and delivery centers and Where we are the transportation service provider, and digital media content costs where we record revenue gross, including video and music."
            ]
        },
        "token_usage": {
            "input_tokens": 5060,
            "output_tokens": 237
        }
    }


Streaming chat
--------------

You can perform streaming chat using :code:`run_stream()` function. Note :code:`SystemPrompts(streaming=True)`, this tells Rhubarb not to respond back with JSON output 
since JSON output in streaming text is hard to parse and re-construct.

.. code:: python
   :emphasize-lines: 5,7

    from rhubarb import DocAnalysis, SystemPrompts

    da = DocAnalysis(file_path="./test_docs/amzn-10k.pdf", 
                     boto3_session=session,
                     system_prompt=SystemPrompts(streaming=True).ChatSysPrompt)

    for resp in da.run_stream(message="What is this document about?"):
        if isinstance(resp, str):
            print(resp,end='')
        else:
            print("\n")
            print(resp)

Sample output

.. code-block:: text

    |-START-|
    Based on the content in these pages, this document appears to be Amazon's annual report or financial statements, specifically discussing the company's results of operations for the fiscal year 2023 compared to 2022.

    The key points covered include:

    - Net sales breakdown by segment - North America, International, and AWS (Amazon Web Services) (Page 1)
    - Operating income/(loss) by segment (Page 2)
    - Detailed operating expenses like cost of sales, fulfillment, technology/infrastructure, marketing etc. (Page 3)
    - Explanations for changes in net sales, operating income, and operating expenses across the different segments (Pages 1-3)

    This report provides an overview of Amazon's financial performance, growth rates, and underlying factors driving the results in its core business segments for the fiscal year.
    |-END-|

    {'input_tokens': 4933, 'output_tokens': 178}