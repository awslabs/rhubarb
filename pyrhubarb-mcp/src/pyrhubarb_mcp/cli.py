# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Rhubarb MCP Server CLI

Command-line interface for running the Rhubarb FastMCP server.
"""

import argparse
import asyncio
import os
import sys
from typing import Optional

from .server import run_server


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="pyrhubarb-mcp",
        description="Run the Rhubarb FastMCP server for document and video understanding",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  AWS_PROFILE             AWS profile name
  AWS_ACCESS_KEY_ID       AWS access key ID
  AWS_SECRET_ACCESS_KEY   AWS secret access key
  AWS_REGION              AWS region (default: us-east-1)
  RHUBARB_ENABLE_CRI      Enable cross-region inference (true/false)
  RHUBARB_DEFAULT_MODEL   Default model to use
  RHUBARB_DEFAULT_BUCKET  Default S3 bucket for classification samples

Examples:
  # Run with default settings
  pyrhubarb-mcp

  # Run with AWS profile (via environment variable)
  AWS_PROFILE=my-profile pyrhubarb-mcp

  # Run with access keys (via environment variables)
  AWS_ACCESS_KEY_ID=AKIA... AWS_SECRET_ACCESS_KEY=secret... pyrhubarb-mcp

  # Run with cross-region inference enabled
  pyrhubarb-mcp --enable-cri

  # Run with custom model and region
  AWS_REGION=us-west-2 pyrhubarb-mcp --default-model nova-pro

Supported Models:
  - claude-opus, claude-sonnet, claude-sonnet-v1, claude-sonnet-v2
  - claude-sonnet-37, claude-haiku
  - nova-pro, nova-lite (for video analysis)

The server exposes the following tools:
  - analyze_document: Document Q&A, summarization, structured extraction
  - stream_document_chat: Streaming chat with conversation history
  - extract_entities: Named entity recognition with 50+ built-in entities
  - generate_extraction_schema: AI-assisted schema generation
  - create_classification_samples: Vector sample creation for classification
  - classify_document: Document classification using vector samples
  - view_classification_sample: View classification sample details
  - analyze_video: Video content analysis (Nova models only)

Resources:
  - rhubarb://entities/built-in: List of built-in entity types
  - rhubarb://models/supported: Supported models and capabilities
  - rhubarb://schemas/built-in/{type}: Built-in schemas
  - rhubarb://classification-samples/{bucket}/{id}: Sample details
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Rhubarb MCP Server 1.0.0"
    )

    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check if all required dependencies are available"
    )

    # Configuration Arguments
    config_group = parser.add_argument_group('Configuration')
    config_group.add_argument(
        "--aws-region",
        default="us-east-1",
        help="AWS region (default: us-east-1)"
    )

    # Rhubarb Configuration Arguments
    rhubarb_group = parser.add_argument_group('Rhubarb Configuration')
    rhubarb_group.add_argument(
        "--enable-cri",
        action="store_true",
        help="Enable cross-region inference"
    )
    rhubarb_group.add_argument(
        "--default-model",
        default="claude-sonnet",
        choices=[
            "claude-opus", "claude-sonnet", "claude-sonnet-v1", "claude-sonnet-v2",
            "claude-sonnet-37", "claude-haiku", "nova-pro", "nova-lite"
        ],
        help="Default model to use (default: claude-sonnet)"
    )
    rhubarb_group.add_argument(
        "--default-bucket",
        help="Default S3 bucket for classification samples"
    )

    return parser


def check_dependencies() -> bool:
    """Check if all required dependencies are available."""
    print("Checking Rhubarb MCP Server dependencies...")

    # Check FastMCP
    try:
        import fastmcp
        print(f"✓ FastMCP: {fastmcp.__version__}")
    except ImportError:
        print("✗ FastMCP: Not installed. Run: pip install fastmcp")
        return False

    # Check Rhubarb core
    try:
        from rhubarb import DocAnalysis, DocClassification
        print("✓ Rhubarb: Core modules available")
    except ImportError as e:
        print(f"✗ Rhubarb: Import error - {e}")
        return False

    # Check VideoAnalysis (may not be available in all environments)
    try:
        from rhubarb import VideoAnalysis
        print("✓ Rhubarb: Video analysis available")
    except ImportError:
        print("⚠ Rhubarb: Video analysis not available (this is OK)")

    # Check AWS credentials
    aws_configured = False
    if os.getenv('AWS_PROFILE'):
        print(f"✓ AWS: Profile configured - {os.getenv('AWS_PROFILE')}")
        aws_configured = True
    elif os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
        print("✓ AWS: Access keys configured")
        aws_configured = True
    else:
        print("⚠ AWS: No credentials configured (server will fail at runtime)")

    # Check boto3
    try:
        import boto3
        session = boto3.Session()
        if aws_configured:
            try:
                # Try to get caller identity to verify credentials work
                sts = session.client('sts')
                identity = sts.get_caller_identity()
                print(f"✓ AWS: Credentials valid - Account: {identity.get('Account', 'unknown')}")
            except Exception as e:
                print(f"⚠ AWS: Credentials may be invalid - {e}")
        print(f"✓ Boto3: Available")
    except ImportError:
        print("✗ Boto3: Not installed. Run: pip install boto3")
        return False

    print("\nDependency check complete!")
    return True


def check_environment() -> Optional[str]:
    """Check the environment and return any warnings."""
    warnings = []

    # Check AWS region
    region = os.getenv('AWS_REGION', 'us-east-1')
    if region != 'us-east-1':
        warnings.append(f"Using AWS region: {region}")

    # Check if CRI is enabled
    if os.getenv('RHUBARB_ENABLE_CRI', 'false').lower() == 'true':
        warnings.append("Cross-region inference is enabled")

    # Check default model
    model = os.getenv('RHUBARB_DEFAULT_MODEL', 'claude-sonnet')
    if model != 'claude-sonnet':
        warnings.append(f"Default model: {model}")

    # Check default bucket
    bucket = os.getenv('RHUBARB_DEFAULT_BUCKET')
    if bucket:
        warnings.append(f"Default S3 bucket: {bucket}")

    return "; ".join(warnings) if warnings else None


async def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.check_deps:
        success = check_dependencies()
        sys.exit(0 if success else 1)

    # Set environment variables from CLI arguments (only for non-AWS settings)
    if args.aws_region:
        os.environ['AWS_REGION'] = args.aws_region
        os.environ['AWS_DEFAULT_REGION'] = args.aws_region  # Set both for compatibility
    
    # Set Rhubarb configuration
    if args.enable_cri:
        os.environ['RHUBARB_ENABLE_CRI'] = 'true'
    if args.default_model:
        os.environ['RHUBARB_DEFAULT_MODEL'] = args.default_model
    if args.default_bucket:
        os.environ['RHUBARB_DEFAULT_BUCKET'] = args.default_bucket

    print("🍃 Starting Rhubarb MCP Server...")

    # Check environment (after setting CLI args)
    env_info = check_environment()
    if env_info:
        print(f"Environment: {env_info}")

    # Show credential configuration
    aws_profile = os.getenv('AWS_PROFILE')
    aws_keys = os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if aws_profile:
        print(f"Using AWS Profile: {aws_profile}")
    elif aws_keys:
        print("Using AWS Access Keys")
    else:
        print("Using environment/default AWS credentials")
    
    print(f"AWS Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    print(f"Default Model: {os.getenv('RHUBARB_DEFAULT_MODEL', 'claude-sonnet')}")

    print("Server capabilities:")
    print("  📄 Document Analysis (PDF, DOCX, images)")
    print("  🎬 Video Analysis (Nova models)")
    print("  🏷️  Entity Recognition & PII Detection")
    print("  📊 Document Classification")
    print("  🔧 Schema Generation")
    print("  💬 Streaming Chat")

    print("\nConnecting to Amazon Bedrock...")

    try:
        # Run the FastMCP server
        await run_server()
    except KeyboardInterrupt:
        print("\n👋 Rhubarb MCP Server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)


def main_sync() -> None:
    """Synchronous wrapper for the main function."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Rhubarb MCP Server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main_sync()
