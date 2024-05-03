<p align="center">
  <img src="./assets/Rhubarb@0.5x.png" alt="Rhubarb" width="400"/>
</p>


<div align="center">

[![Amazon Bedrock](https://img.shields.io/badge/Amazon%20Bedrock-8A2BE2?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALUAAAC1BAMAAADrfaOaAAAAD1BMVEUAAAD///////////////+PQt5oAAAABHRSTlMAgL9ARyeO/QAABIpJREFUeNrt22GSmyAUwHGJPUBsOEC6cgBicoCq3P9MrRryT5CAGJxuZ3yftqbz61t44QlMiz322GOPPfb4XlHqYqsojamKbaJUxpj2WGwRA222SV2O8iapN4aoNqB7ITdIXYzi3x+q7KmXA9eN1f1IXWerPkuTep+x+qYhJvUuX/XVz08q125Ut2oGGk+WQr08udmpTqaxCfn85GDGOKZXX9y2pbOq+lTQFuYeek31yaD9w5juKpQx5zXVF7blONSCkk+pvoitppFWSSUvJjpmG/N7KsQuMe2+iNnlYE/Dnma3xRL7vMrWC2w7JsttgPh4tzzKZVOoepz4Nr99G1U5DE12+zAtC8Yc89ulYT1bb1+vemaPgzLG+SObIcUegiaX3xaSXp3PZjqPxW7/D/alOm1h29jt3f52tvl6CpVsK2fhLJ9tJxJt6b5Ty2x2Y1/YeRCydRr9iguyc+zUTcPB2Dg9vebXBXb1Ejrx9bjTklwZfUroo51w+cCb6cF6G9qSYqoBBvtj29IWb68MNvbnm2xBJSy2r6dgiZDkZaI7HbcZ0e647Pso72O+1FaBepd8Al4XS+0DQxjY5pAJUtyWoUVAzqUEW9g3/XPQbvQK+4fdobQhuzHnFbacpt2YLmCz+ffa5ssfY8LsNue2rdKA/T7a+9Bov22XFJ1s2/5xeGuzWq2wezq/z2ZJWWv/eDvejaUDduWP+/dMvrGZkhU1eLMnTP769jX4NmqznHSnYbr6t3annY5/WmiXwRcW+UoL/m7KWtW9/RCoVCQSt8ml9tszursojtOxA4kzP8GzVvp8G7SJSnW1jtn0zgnvozYRt8Vj5H4y4jlsDkT5puW0b1SjbDPbQvPjOatNxPvOL53Nnkef3ya2tM8b2m02u3KC1p1gl78W/PsLD3vl7D1eezaIna/hRO3brKOdZ7TPGTb1sUu7w8vFqnAnyW4QPTlNUUeL4EhvwOaRxxY0qDhO85zT2IRaUovCsGUlj1ivZZ+uo3h7b2X1/AyhdmuQS7sLX9AgzmA7tFPfaZd2TEynPRf1ftssvbSTTPrsDMGx0y7twGsf7dhJl1/grac2Z33nlHZpx2XWfB7na6xOzJtf3KFdm5rjtjPJpkQCthoTFolNgnkM2Fza9Uk29LzvPOzD8ItxabfQpkT8d7qpl3YAzGPIZqTq5TZ02ObSbrFNicRtoZiUBTbzGLRtXK5pL50COmAnBQDH8vntG/OY3T5A57SJf2H/ZFeb2WYXnN8W7Eey24rWk9sWLOEf2+WRj+yrlKYdfGKXqucj54T0M5sn2JyQfmg390njIxU4IU3a+Ag7adiBE9KkjQ9vtdjBE9Loxufo7fSMSb9iTGju/AEBmxPS9XhzH2xsTkjL1Bpktzfgwn/6exiGqWTSk/GWeXRs54R0Fc48zr9EUxRr4qfnRhibE9JVIT0rXanSe0N84zM/K6iM+dLFetw5WXZSXS2zSybpWRf7GCdpiiYbTtKmzkNTie0j6Wv+/4KQP2lwks6Nk3T2EFskDU7S+fFrsccee+yxxx7fP/4AG81mLMegln0AAAAASUVORK5CYII=)](https://aws.amazon.com/bedrock/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-311/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

</div>

<!-- [![PyPI pyversions](https://img.shields.io/pypi/pyversions/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/) -->

# Rhubarb

Rhubarb is a light-weight Python framework that makes it easy to build document understanding applications using Multi-modal Large Language Models (LLMs) and Embedding models. Rhubarb is created from the ground up to work with Amazon Bedrock and Anthropic Claude V3 Multi-modal Language Models, and Amazon Titan Multi-modal Embedding model.

## What can I do with Rhubarb?

Visit Rhubarb [documentation](https://awslabs.github.io/rhubarb/index.html#).

Rhubarb can do multiple document processing tasks such as

- ✅ Document Q&A
- ✅ Streaming chat with documents (Q&A)
- ✅ Document Summarization
  - 🚀 Page level summaries
  - 🚀 Full summaries
  - 🚀 Summaries of specific pages
  - 🚀 Streaming Summaries
- ✅ Structured data extraction
- ✅ Named entity recognition (NER) 
  - 🚀 With 50 built-in common entities
- ✅ PII recognition with built-in entities
- ✅ Figure and image understanding from documents
  - 🚀 Explain charts, graphs, and figures
  - 🚀 Perform table reasoning (as figures)
- ✅ Document Classification with vector sampling using multi-modal embedding models
- ✅ Logs token usage to help keep track of costs

Rhubarb comes with built-in system prompts that makes it easy to use it for a number of different document understanding use-cases. You can customize Rhubarb by passing in your own system prompts. It supports exact JSON schema based output generation which makes it easy to integrate into downstream applications.

- Supports PDF, TIFF, PNG, JPG files (support for Word, Excel, PowerPoint, CSV, Webp, eml files coming soon)
- Performs document to image conversion internally to work with the multi-modal models
- Works on local files or files stored in S3
- Supports specifying page numbers for multi-page documents
- Supports chat-history based chat for documents
- Supports streaming and non-streaming mode

## Installation

Start by installing Rhubarb using `pip`.

```
pip install pyrhubarb
```


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

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.