.. Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

   This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0
   International License (the "License"). You may not use this file except in compliance with the
   License. A copy of the License is located at http://creativecommons.org/licenses/by-nc-sa/4.0/.

   This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
   either express or implied. See the License for the specific language governing permissions and
   limitations under the License.

.. _aws-boto3-examples:

Video Analysis
=============

Rhubarb supports video analysis using Amazon Bedrock's Nova models. This feature allows you to extract insights, summaries, and information from video content.

Requirements
-----------

- Videos must be stored in Amazon S3
- Only Amazon Nova models (NOVA_PRO or NOVA_LITE) are supported
- A valid boto3 session with appropriate permissions

Basic Usage
----------

.. code-block:: python

    from rhubarb import VideoAnalysis
    import boto3

    session = boto3.Session()

    va = VideoAnalysis(
        file_path="s3://my-bucket/my-video.mp4",
        boto3_session=session
    )

    # Ask a question about the video
    response = va.run(message="What is the main topic of this video?")

Available Methods
---------------

- ``run(message)``: Ask any question about the video
- ``run_stream(message)``: Stream the response to any question about the video

Asking Specific Questions
--------------------

You can ask specific questions about the video content:

.. code-block:: python

    import boto3
    from rhubarb import VideoAnalysis, LanguageModels

    # Create a boto3 session
    session = boto3.Session()

    # Initialize video analysis with a video in S3
    va = VideoAnalysis(
        file_path="s3://my-bucket/my-video.mp4",
        boto3_session=session,
        modelId=LanguageModels.NOVA_PRO  # For higher quality analysis
    )

    # Ask questions about the video
    response = va.run(message="What is happening in this video?")
    print(response)
    
    # Ask about specific aspects of the video
    summary_response = va.run(message="Provide a comprehensive summary of this video")
    print(summary_response)
    
    entities_response = va.run(message="What people, objects, and locations appear in this video?")
    print(entities_response)
    
    actions_response = va.run(message="Describe the main actions and movements in this video")
    print(actions_response)
    
    text_response = va.run(message="Extract any visible text from this video")
    print(text_response)

Streaming Responses
------------------

For faster feedback, you can stream the responses:

.. code-block:: python

    # Stream responses for better user experience
    for chunk in va.run_stream(message="Analyze this video in detail"):
        if "response" in chunk:
            print(chunk["response"], end="")

Using Different Models
--------------------

You can specify which Nova model to use for video analysis:

.. code-block:: python

    from rhubarb import VideoAnalysis, LanguageModels
    
    # Use Nova Pro for higher quality analysis
    va = VideoAnalysis(
        file_path="s3://my-bucket/my-video.mp4",
        boto3_session=session,
        modelId=LanguageModels.NOVA_PRO
    )

    # Use Nova Lite for faster, more economical analysis
    va_lite = VideoAnalysis(
        file_path="s3://my-bucket/my-video.mp4",
        boto3_session=session,
        modelId=LanguageModels.NOVA_LITE
    )

Configuration Options
------------------

- ``modelId``: Choose between NOVA_PRO and NOVA_LITE (default: NOVA_LITE)
- ``system_prompt``: Customize the system prompt for specialized analysis
- ``max_tokens``: Control the length of the generated response
- ``temperature``: Adjust the creativity of the responses
- ``frame_interval``: Set the interval between frames in seconds
- ``max_frames``: Limit the maximum number of frames to extract
- ``use_converse_api``: Enable Bedrock's converse API for tool use
- ``enable_cri``: Enable Cross-region inference
- ``s3_bucket_owner``: Specify the AWS account ID for cross-account S3 access

Advanced Configuration
--------------------

Configure additional parameters for video analysis:

.. code-block:: python

    va = VideoAnalysis(
        file_path="s3://my-bucket/my-video.mp4",
        boto3_session=session,
        modelId=LanguageModels.NOVA_PRO,
        max_tokens=2048,           # Control response length
        temperature=0.2,           # Adjust creativity
        use_converse_api=True,     # Use Bedrock's converse API
        enable_cri=True,           # Enable cross-region inference
        s3_bucket_owner="123456789012"  # For cross-account S3 access
    )

Limitations
---------

- Currently only supports videos stored in Amazon S3
- Requires Amazon Nova models (NOVA_PRO or NOVA_LITE)
- Video processing capabilities are determined by the underlying model's capabilities