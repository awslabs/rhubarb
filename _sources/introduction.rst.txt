Introduction
============

**Rhubarb** can perform multiple document and video processing and understanding tasks. Fundamentally, Rhubarb uses Multi-modal language
models and multi-modal embedding models available via Amazon Bedrock to perform document extraction, summarization, Entity detection, Q&A, video analysis and more. 
Rhubarb comes with built-in system prompts that makes it easy to use it for a number of different understanding use-cases. You can customize 
Rhubarb by passing in your own system and user prompts. It supports deterministic JSON schema based output generation which makes 
it easy to integrate into downstream applications.

Features
--------

Document Processing
~~~~~~~~~~~~~~~~~~

- Document Q&A
- Streaming chat with documents (Q&A)
- Document Summarization
   - Page level summary
   - Full summary
   - Summaries of specific pages
   - Streaming Summary
- Extraction based on a JSON schema
   - Key-value extractions
   - Table extractions
- Named entity recognition (NER) 
   - With 50 built-in common entities
- PII recognition with built-in entities
- Figure and image understanding from documents
   - Explain charts, graphs, and figures
   - Perform table reasoning (as figures)
- Document Classification with vector sampling using multi-modal embedding models
- Auto generation of JSON schema from natural language prompts for document extraction
- Logs token usage to help keep track of costs

Video Analysis
~~~~~~~~~~~~~

- Video summarization
- Entity extraction from videos
- Action and movement analysis
- Text extraction from video frames
- Streaming video analysis responses


Things to know
--------------

In it's current form Rhubarb-

1. Supports PDF, TIFF, PNG, DOCX, JPG files for document processing
2. Supports MP4, AVI, MOV, and other common video formats for video analysis (S3 storage required)
3. Performs document to image conversion internally to work with the multi-modal models
4. Works on local files or files stored in S3 (video analysis requires S3 storage)
5. Supports specifying page numbers for multi-page documents
6. Supports chat-history based chat for documents
7. Supports streaming and non-streaming mode
8. Supports Converse API
9. Supports Cross-Region Inference