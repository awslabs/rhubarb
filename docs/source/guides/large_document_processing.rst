Large Document Processing
=======================

Rhubarb now supports processing documents with more than 20 pages using a sliding window approach. This feature is particularly useful when working with Claude models, which have a limitation of processing only 20 pages at a time.

How it works
-----------

The sliding window technique works by:

1. Breaking the document into chunks of 20 pages (Claude's maximum page limit)
2. Processing each chunk separately
3. Combining the results from all chunks
4. Making an additional call to Bedrock to synthesize all outputs from the sliding windows into one consolidated response

When enabled, Rhubarb will automatically handle the chunking, processing, and synthesis of large documents, making it seamless to work with documents of any size. Note that the additional Bedrock call for synthesis will incur extra costs beyond the calls for each window.

Enabling Sliding Window Processing
---------------------------------

To enable the sliding window approach, set the ``sliding_window_overlap`` parameter when creating a ``DocAnalysis`` object:

.. code-block:: python

    from rhubarb import DocAnalysis
    import boto3

    session = boto3.Session()

    doc_analysis = DocAnalysis(
        file_path="path/to/large-document.pdf",
        boto3_session=session,
        sliding_window_overlap=2     # Number of pages to overlap between windows (1-10)
    )

The ``sliding_window_overlap`` parameter determines how many pages will overlap between consecutive windows. This overlap helps maintain context between chunks and ensures that information that spans page boundaries is not lost.

Processing a Large Document
--------------------------

Once you've created a ``DocAnalysis`` object with sliding window enabled, you can use it just like you would with smaller documents:

.. code-block:: python

    # Ask a question about the document
    response = doc_analysis.run("What are the main points discussed in this document?")

    # Summarize the document
    summary = doc_analysis.summarize()

    # Extract information using a schema
    extracted_data = doc_analysis.extract(schema=my_schema)

Understanding the Response
-------------------------

When using the sliding window approach, the response will include a synthesized result from all windows and the individual window results:

.. code-block:: json

    {
        "synthesized_response": "The document discusses...",
        "window_results": [
            {
                "answer": "In pages 1-20, the document covers...",
                "window_info": {
                    "total_pages": 45,
                    "current_window_start": 1,
                    "current_window_end": 20,
                    "current_window_size": 20,
                    "has_previous_window": false,
                    "has_next_window": true
                }
            },
            {
                "answer": "In pages 18-37, the document discusses...",
                "window_info": {
                    "total_pages": 45,
                    "current_window_start": 18,
                    "current_window_end": 37,
                    "current_window_size": 20,
                    "has_previous_window": true,
                    "has_next_window": true
                }
            },
            {
                "answer": "In pages 35-45, the document concludes with...",
                "window_info": {
                    "total_pages": 45,
                    "current_window_start": 35,
                    "current_window_end": 45,
                    "current_window_size": 11,
                    "has_previous_window": true,
                    "has_next_window": false
                }
            }
        ]
    }

Current Limitations
------------------

While the sliding window approach allows processing of large documents, there are some limitations to be aware of:

1. **Classification**: The sliding window technique is not yet supported for document classification. When using classification with large documents, only the first 20 pages will be considered.

2. **Context Across Windows**: Although overlap helps maintain some context between windows, information that spans across multiple windows might not be fully captured in responses that require understanding the entire document.

3. **Performance**: Processing large documents with the sliding window approach will take longer and consume more tokens compared to processing smaller documents.

4. **Cost**: The additional Bedrock call required to synthesize results from all windows will increase the overall cost of processing large documents compared to processing a single document of 20 pages or less.

For more examples and detailed usage, see the `Large Document Processing Cookbook <https://github.com/awslabs/rhubarb/blob/main/cookbooks/2-large-document-processing.ipynb>`_.
