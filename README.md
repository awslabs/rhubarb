<p align="center">
  <img src="./assets/Rhubarb@0.5x.png" alt="Rhubarb" width="400"/>
</p>


[![Amazon Bedrock](https://img.shields.io/badge/Amazon%20Bedrock-8A2BE2?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALUAAAC1AQMAAAAjnSzqAAAAA1BMVEX///+nxBvIAAAAGklEQVRYw+3BAQ0AAADCIPuntscHDAAAACDqEPgAASGiEMoAAAAASUVORK5CYII=)](https://aws.amazon.com/bedrock/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-311/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<!-- [![PyPI pyversions](https://img.shields.io/pypi/pyversions/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/) -->

# Rhubarb

Rhubarb is a light-weight Python framework that makes it easy to build document understanding applications using Multi-modal Large Language Models (LLMs) and Embedding models. Rhubarb is created from the gorund up to work with Amazon Bedrock and Anthropic Claude V3 Multi-modal Language Models, and Amazon Titan Multi-modal Embedding model.

## What can I do with Rhubarb?

Rhubarb can do multiple document processing tasks such as

- ✅ Document Q&A
- ✅ Streaming chat with documents (Q&A)
- ✅ Document Summarization
  - 🚀 Page level summaries
  - 🚀 Full summaries
  - 🚀 Summaries of specific pages
  - 🚀 Streaming Summaries
- ✅ Extraction based on a JSON schema
  - 🚀 Key-value extractions
  - 🚀 Table extractions
- ✅ Named entity recognition (NER) 
  - 🚀 With 50 built-in common entities
- ✅ PII recognition with built-in entities
- ✅ Figure and image understanding from documents
  - 🚀 Explain charts, graphs, and figures
  - 🚀 Perform table reasoning (as figures)
- ✅ Document Classification with vector sampling using multi-modal embedding models
- ✅ Auto generation of JSON schema from natural language prompts for document extraction
- ✅ Logs token usage to help keep track of costs

Rhubarb comes with built-in system prompts that makes it easy to use it for a number of different document understanding use-cases. You can customize Rhubarb by passing in your own system prompts. It supports exact JSON schema based output generation which makes it easy to integrate into downstream applications.

- Supports PDF, TIFF, PNG, JPG files
- Performs document to image conversion internally to work with the multi-modal models
- Works on local files or files stored in S3
- Supports specifying page numbers for multi-page documents
- Supports chat-history based chat for documents
- Supports streaming and non-streaming mode

## Installation

Start by installing Rhubarb using `pip`. Rhubarb is currently available in Test PyPi which you can install as follows

```
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ rhubarb_dev
```
<!-- 
 Once it is available in PyPi main index, you would be able to install normally. 

```
pip install rhubarb 
```
-->


### Usage

Create a `boto3` session.

```python
import boto3
session = boto3.Session()
```

#### Call Rhubarb

Local file

```python
from rhubarb import DocAnalysis

da = DocAnalysis(file_path="./path/to/doc/doc.pdf", 
                 boto3_session=session)
resp = da.run(message="What is the employee's name?")
resp
```

With file in Amazon S3

```python
from rhubarb import DocAnalysis

da = DocAnalysis(file_path="s3://path/to/doc/doc.pdf", 
                 boto3_session=session)
resp = da.run(message="What is the employee's name?")
resp
```

For more usage examples see [cookbooks](./cookbooks/).

## License

Apache License 2.0