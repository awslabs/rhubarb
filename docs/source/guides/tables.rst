Tables Extraction
=================

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
