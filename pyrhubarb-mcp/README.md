# Rhubarb MCP Server

A dedicated MCP server package that exposes all of [Rhubarb's](https://github.com/awslabs/rhubarb) document and video understanding capabilities through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

This is a standalone package designed for easy integration with MCP-compatible AI assistants like Cline, Claude Desktop, and other MCP clients.

## ✨ Features

### 🔧 Tools (8 total)
- **`analyze_document`** - Multi-modal document Q&A, summarization, structured extraction
- **`stream_document_chat`** - Streaming conversations with chat history
- **`extract_entities`** - Named Entity Recognition with 50+ built-in entities + PII detection
- **`generate_extraction_schema`** - AI-assisted JSON schema generation
- **`create_classification_samples`** - Vector sample creation for document classification
- **`classify_document`** - Document classification using pre-trained samples  
- **`view_classification_sample`** - Classification sample inspection
- **`analyze_video`** - Video content analysis with Amazon Nova models

### 📚 Resources (4 available)
- **`rhubarb://entities/built-in`** - List of 50+ built-in entity types
- **`rhubarb://models/supported`** - Supported Bedrock models and capabilities
- **`rhubarb://schemas/built-in/{type}`** - Built-in schemas for common use cases
- **`rhubarb://classification-samples/{bucket}/{id}`** - Classification sample details

## 🚀 Quick Start

### No Installation Required!

The MCP server automatically installs when first used through `uvx` or `pipx`:

```bash
# Test the server (optional)
uvx pyrhubarb-mcp@latest --check-deps

# Run with AWS profile (via environment variable)
AWS_PROFILE=my-profile uvx pyrhubarb-mcp@latest

# Run with access keys (via environment variables)
AWS_ACCESS_KEY_ID=AKIA... AWS_SECRET_ACCESS_KEY=secret... uvx pyrhubarb-mcp@latest
```

## 🔧 MCP Client Configuration

### Cline Integration
```json
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
```

### Claude Desktop Integration
```json
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
```

### Using Access Keys (for CI/CD)
```json
{
  "rhubarb": {
    "command": "uvx",
    "args": [
      "pyrhubarb-mcp@latest",
      "--aws-region", "us-west-2",
      "--default-model", "nova-pro"
    ],
    "env": {
      "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
      "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }
  }
}
```

### Alternative: Using pipx
```json
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
```

## 📋 Configuration Options

### Command-Line Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `--aws-region` | AWS region | `us-east-1` |
| `--enable-cri` | Enable cross-region inference | `false` |
| `--default-model` | Default model | `claude-sonnet` |
| `--default-bucket` | S3 bucket for classification samples | - |
| `--check-deps` | Check dependencies and exit | - |

### Environment Variables (AWS Credentials)
| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_PROFILE` | AWS profile name | `my-profile` |
| `AWS_ACCESS_KEY_ID` | AWS access key ID | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key | `wJalrXUtnFEMI/K7MDENG...` |
| `AWS_REGION` | AWS region (can also use CLI arg) | `us-east-1` |

### Supported Models
| Model | Documents | Video | Best For |
|-------|-----------|-------|----------|
| `claude-opus` | ✅ | ❌ | Complex reasoning, detailed analysis |
| `claude-sonnet` | ✅ | ❌ | Balanced performance and cost |
| `claude-haiku` | ✅ | ❌ | Fast, lightweight tasks |
| `nova-pro` | ✅ | ✅ | High-quality video analysis |
| `nova-lite` | ✅ | ✅ | Cost-effective video processing |

## 💡 Usage Examples

Once configured, ask your AI assistant to use Rhubarb's tools:

### Document Analysis
```
Use the analyze_document tool on s3://my-bucket/report.pdf to extract:
- Key findings
- Recommendations  
- Financial data

Structure the output as JSON with those three categories.
```

### Entity Extraction
```
Use extract_entities on ./contract.pdf to find all:
- PERSON entities
- ORGANIZATION entities  
- MONEY amounts
- Important dates
- Any PII information
```

### Video Analysis
```
Use analyze_video on s3://my-bucket/presentation.mp4 to:
- Summarize key points
- Extract any text shown on screen
- Identify main topics discussed
```

### Document Classification
```
First create classification samples from ./training_manifest.csv in bucket 'my-docs'.
Then classify ./unknown_document.pdf using those samples.
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │────│ pyrhubarb-mcp    │────│   pyrhubarb     │
│  (Cline, etc.)  │    │   (MCP Server)   │    │  (Core Library) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                               ┌─────────────────┐
                                               │  Amazon Bedrock │
                                               │ (Claude & Nova) │
                                               └─────────────────┘
```

### Key Benefits
- **🔌 Plug & Play** - No pre-installation, auto-installs on first use
- **🐍 Native Python** - Direct access to Rhubarb capabilities  
- **💬 Conversation Memory** - Maintains chat history across interactions
- **🔍 Resource Discovery** - Built-in resources for exploration
- **⚡ High Performance** - Optimized for large documents and video processing

## 🛠️ Development

### Local Development
```bash
# Clone and install
git clone https://github.com/awslabs/rhubarb.git
cd rhubarb/pyrhubarb-mcp
poetry install

# Run locally  
poetry run pyrhubarb-mcp --check-deps
```

### Dependencies
This package automatically installs:
- **`pyrhubarb`** - Core Rhubarb document/video processing
- **`fastmcp`** - MCP server framework
- **`boto3`** - AWS SDK for Python

## 🔐 Security & Requirements

### AWS Credentials
Requires AWS credentials with permissions for:
- **Amazon Bedrock** - For Claude and Nova model access
- **Amazon S3** - For document/video storage (optional but recommended)

### Supported Regions
Works in any AWS region with Amazon Bedrock availability. Commonly used regions:
- `us-east-1` (N. Virginia) - Default, supports all models
- `us-west-2` (Oregon) - All models available  
- `eu-west-1` (Ireland) - Most models available

## 📚 Related Links

- **[Rhubarb Documentation](https://awslabs.github.io/rhubarb/)** - Complete docs for the core library
- **[Rhubarb GitHub](https://github.com/awslabs/rhubarb)** - Source code and examples
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Learn about MCP
- **[FastMCP](https://github.com/jlowin/fastmcp)** - The MCP framework we use

## 📄 License

Apache 2.0 - See [LICENSE](../LICENSE) for details.

## 🤝 Contributing  

This package is part of the larger Rhubarb project. Please see the main [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.
