MCP Server Integration
======================

Rhubarb includes a dedicated **pyrhubarb-mcp package** that provides a FastMCP server exposing all document and video understanding capabilities through the `Model Context Protocol (MCP) <https://modelcontextprotocol.io/>`_. This allows seamless integration with MCP-compatible AI assistants like Cline, Claude Desktop, and other MCP clients.

What is MCP?
------------

The Model Context Protocol (MCP) is an open standard for connecting AI assistants to external tools and data sources. MCP enables:

- **Universal Tool Access**: AI assistants can use external tools consistently
- **Secure Integration**: Controlled access to resources and capabilities  
- **Extensible Architecture**: Easy addition of new tools and resources

Rhubarb's MCP server provides native access to all document processing capabilities without requiring separate API integration.

Features
--------

Tools (8 Available)
~~~~~~~~~~~~~~~~~~~

.. list-table:: Available MCP Tools
   :widths: 25 35 40
   :header-rows: 1

   * - Tool Name
     - Description  
     - Capabilities
   * - ``analyze_document``
     - Multi-modal document analysis
     - Q&A, summarization, structured extraction
   * - ``stream_document_chat``
     - Streaming conversations
     - Chat with conversation history
   * - ``extract_entities``
     - Entity recognition
     - 50+ built-in entities + custom entities + PII
   * - ``generate_extraction_schema``
     - AI schema generation
     - Custom JSON schemas for extraction
   * - ``create_classification_samples``
     - Vector sample creation
     - Document classification training
   * - ``classify_document``
     - Document classification
     - Classify using pre-trained samples
   * - ``view_classification_sample``
     - Sample inspection
     - View classification details
   * - ``analyze_video``
     - Video understanding
     - Nova model video analysis

Resources (4 Available)
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Available MCP Resources
   :widths: 40 60
   :header-rows: 1

   * - Resource URI
     - Description
   * - ``rhubarb://entities/built-in``
     - List of 50+ built-in entity types for Named Entity Recognition
   * - ``rhubarb://models/supported``
     - Supported Bedrock models and their capabilities
   * - ``rhubarb://schemas/built-in/{type}``
     - Built-in schemas for common document processing use cases
   * - ``rhubarb://classification-samples/{bucket}/{id}``
     - Classification sample details including classes and sample counts

Installation & Setup
--------------------

Prerequisites
~~~~~~~~~~~~~

1. **Python 3.11+** - Required for the MCP server
2. **AWS Credentials** - Required for Amazon Bedrock and S3 access
3. **pipx or uvx** - For auto-installing the MCP server

No manual installation is required - the MCP server auto-installs when first used.

Quick Start
~~~~~~~~~~~

1. **No installation required** - The MCP server auto-installs when first used through uvx or pipx

2. **Test the server** (optional)::

    uvx pyrhubarb-mcp@latest --check-deps

3. **Configure AWS credentials via environment variables**::

    # With AWS Profile
    AWS_PROFILE=your-profile uvx pyrhubarb-mcp@latest
    
    # With Access Keys  
    AWS_ACCESS_KEY_ID=AKIA... AWS_SECRET_ACCESS_KEY=secret... uvx pyrhubarb-mcp@latest

The server will start automatically when your MCP client connects to it.

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

The MCP server is configured through environment variables:

.. list-table:: Environment Variables
   :widths: 30 50 20
   :header-rows: 1

   * - Variable
     - Description
     - Default
   * - ``AWS_REGION``
     - AWS region for Bedrock and S3 access
     - ``us-east-1``
   * - ``AWS_PROFILE``
     - AWS profile name to use
     - *None*
   * - ``AWS_ACCESS_KEY_ID``
     - AWS access key ID
     - *None*
   * - ``AWS_SECRET_ACCESS_KEY``
     - AWS secret access key
     - *None*
   * - ``RHUBARB_ENABLE_CRI``
     - Enable cross-region inference
     - ``false``
   * - ``RHUBARB_DEFAULT_MODEL``
     - Default model to use
     - ``claude-sonnet``
   * - ``RHUBARB_DEFAULT_BUCKET``
     - Default S3 bucket for classification samples
     - *None*

Command-Line Arguments
~~~~~~~~~~~~~~~~~~~~~~

The server supports additional configuration through command-line arguments:

.. code-block:: bash

   pyrhubarb-mcp --help

Available arguments:

- ``--aws-region`` - AWS region (overrides environment)
- ``--enable-cri`` - Enable cross-region inference  
- ``--default-model`` - Default model selection with validation
- ``--default-bucket`` - Default S3 bucket for classification samples
- ``--check-deps`` - Check all dependencies and AWS credentials

MCP Client Configuration
------------------------

The MCP server integrates with various MCP-compatible clients. Here are configuration examples for popular clients:

Cline Integration
~~~~~~~~~~~~~~~~~

Add to your Cline MCP settings using uvx (no pre-installation required):

**Option 1: Using AWS Profile (Recommended)**

.. code-block:: json

   {
     "rhubarb": {
       "command": "uvx",
       "args": [
         "pyrhubarb-mcp@latest",
         "--aws-region", "us-east-1",
         "--default-model", "claude-sonnet"
       ],
       "env": {
         "AWS_PROFILE": "your-aws-profile"
       }
     }
   }

**Option 2: Using AWS Access Keys**

.. code-block:: json

   {
     "rhubarb": {
       "command": "uvx",
       "args": [
         "pyrhubarb-mcp@latest",
         "--aws-region", "us-west-2",
         "--default-model", "claude-sonnet"
       ],
       "env": {
         "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
         "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
       }
     }
   }

**Option 3: Advanced Configuration**

.. code-block:: json

   {
     "rhubarb": {
       "command": "uvx",
       "args": [
         "pyrhubarb-mcp@latest",
         "--aws-region", "us-west-2", 
         "--default-model", "nova-pro",
         "--enable-cri",
         "--default-bucket", "my-classification-bucket"
       ],
       "env": {
         "AWS_PROFILE": "production"
       }
     }
   }

Claude Desktop Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Add to your Claude Desktop configuration:

.. code-block:: json

   {
     "mcpServers": {
       "rhubarb": {
         "command": "uvx",
         "args": [
           "pyrhubarb-mcp@latest",
           "--default-model", "claude-sonnet"
         ],
         "env": {
           "AWS_PROFILE": "your-aws-profile"
         }
       }
     }
   }

Alternative with pipx
~~~~~~~~~~~~~~~~~~~~~

You can also use pipx instead of uvx:

.. code-block:: json

   {
     "rhubarb": {
       "command": "pipx",
       "args": [
         "run", "pyrhubarb-mcp@latest",
         "--default-model", "claude-sonnet"
       ],
       "env": {
         "AWS_PROFILE": "your-profile"
       }
     }
   }

Usage Examples
--------------

Once configured, you can use Rhubarb's capabilities directly through your MCP client:

Document Analysis
~~~~~~~~~~~~~~~~~

Ask your AI assistant to analyze a document::

   "Use the analyze_document tool to analyze this PDF: s3://my-bucket/report.pdf
   Ask: 'What are the key findings in this report?'"

The tool will return structured analysis results from the document.

Entity Extraction
~~~~~~~~~~~~~~~~~

Extract entities from documents::

   "Use the extract_entities tool on ./invoice.pdf to find all ORGANIZATION, 
   MONEY, and DATE entities, plus any PII information"

Video Analysis
~~~~~~~~~~~~~~

Analyze video content::

   "Use the analyze_video tool on s3://my-bucket/presentation.mp4 to summarize 
   the key points from this presentation using the nova-pro model"

Document Classification
~~~~~~~~~~~~~~~~~~~~~~~

Classify documents using pre-trained samples::

   "First, use create_classification_samples with ./training_manifest.csv 
   and bucket my-classification-bucket. Then classify ./unknown_document.pdf 
   using those samples."

Advanced Features
-----------------

Conversation Memory
~~~~~~~~~~~~~~~~~~~

The server maintains conversation history for document chat sessions::

   "Start a streaming chat with ./document.pdf about the financial data"
   # Follow-up questions will maintain context

Schema Generation
~~~~~~~~~~~~~~~~~

Generate custom extraction schemas::

   "Use generate_extraction_schema on ./sample_contract.pdf to create a schema 
   for extracting: parties involved, contract dates, payment terms, and obligations"

Resource Discovery
~~~~~~~~~~~~~~~~~~

Access built-in resources for information::

   "Show me the rhubarb://entities/built-in resource to see all available entity types"
   "Check rhubarb://models/supported for available models and their capabilities"

Supported Models
----------------

The MCP server supports all Rhubarb-compatible models:

.. list-table:: Model Support
   :widths: 20 15 15 50
   :header-rows: 1

   * - Model
     - Documents  
     - Video
     - Use Cases
   * - ``claude-opus``
     - ✅
     - ❌
     - Complex reasoning, detailed analysis
   * - ``claude-sonnet`` 
     - ✅
     - ❌
     - Balanced performance and cost
   * - ``claude-sonnet-v1``
     - ✅
     - ❌
     - Legacy compatibility
   * - ``claude-sonnet-v2``
     - ✅
     - ❌  
     - Latest Claude features
   * - ``claude-sonnet-37``
     - ✅
     - ❌
     - Enhanced capabilities
   * - ``claude-haiku``
     - ✅
     - ❌
     - Fast, lightweight tasks
   * - ``nova-pro``
     - ✅
     - ✅
     - High-quality video analysis
   * - ``nova-lite``
     - ✅
     - ✅
     - Cost-effective video processing

Architecture
------------

The MCP server provides a clean integration layer:

.. code-block:: text

   ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
   │   MCP Client    │────│  FastMCP Server  │────│  Rhubarb Core   │
   │  (Cline, etc.)  │    │   (Python)       │    │   (Python)      │
   └─────────────────┘    └──────────────────┘    └─────────────────┘
                                  │                         │
                                  │                         │
                          ┌──────────────────┐    ┌─────────────────┐
                          │   Conversation   │    │  Amazon Bedrock │
                          │     Memory       │    │   (Claude, Nova) │
                          └──────────────────┘    └─────────────────┘
                                                           │
                                                  ┌─────────────────┐
                                                  │   Amazon S3     │
                                                  │ (Documents, etc.)│
                                                  └─────────────────┘

Key Benefits:

- **Native Python**: No external bridge, direct Rhubarb integration
- **Full Feature Parity**: All Rhubarb capabilities exposed through MCP  
- **Conversation Memory**: Maintains chat history across interactions
- **Resource Discovery**: Built-in resources for entities, models, schemas
- **Error Handling**: Comprehensive error reporting and validation

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**"FastMCP not installed"**::

   poetry install  # Reinstall dependencies

**"AWS credentials not configured"**::

   export AWS_PROFILE=your-profile
   # or
   export AWS_ACCESS_KEY_ID=your-key AWS_SECRET_ACCESS_KEY=your-secret

**"Bedrock access denied"**

- Ensure your AWS credentials have Amazon Bedrock permissions
- Verify the region supports the requested models
- Check your AWS account has access to Bedrock models

**"Video analysis requires S3"**

- Video files must be stored in Amazon S3
- Use ``s3://bucket/video.mp4`` format
- Ensure S3 bucket permissions allow access

Debug Mode
~~~~~~~~~~

Run with verbose output for troubleshooting::

   DEBUG=1 pyrhubarb-mcp

This will provide detailed logging for diagnosis.

Dependency Checking
~~~~~~~~~~~~~~~~~~~

Verify your setup with the dependency checker::

   pyrhubarb-mcp --check-deps

This checks:
- FastMCP installation
- Rhubarb core modules  
- AWS credential configuration
- Boto3 availability
- AWS account access

Performance Considerations
--------------------------

- **Large Documents**: Use ``sliding_window_overlap`` parameter for documents >20 pages
- **Video Processing**: Nova models have frame limits (default: 20 frames)
- **Classification**: Vector samples are cached in S3 for fast retrieval  
- **Memory Management**: Conversations are kept in memory (restart server to clear)

Security
--------

- **Credential Handling**: AWS credentials are never logged or exposed
- **S3 Access**: Ensure proper bucket permissions and access policies
- **Input Validation**: All tool inputs are validated before processing
- **Error Handling**: Sensitive information is filtered from error messages

For production deployments, follow AWS security best practices for credential management and access control.
