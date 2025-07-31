Office Document Processing
=========================

Rhubarb now supports Microsoft Office formats including Excel spreadsheets and PowerPoint presentations, in addition to the existing support for Word documents.

.. note::
   Office format processing requires additional dependencies that are automatically installed with Rhubarb: ``openpyxl``, ``python-pptx``, and ``matplotlib``.

Supported Office Formats
------------------------

Excel Support (.xlsx, .xls)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rhubarb can process Excel spreadsheets with intelligent handling for large files:

- **Automatic worksheet detection**: Processes all worksheets in a workbook
- **Large file chunking**: Automatically breaks large spreadsheets into manageable sections
- **Visual rendering**: Converts spreadsheet data into formatted PNG images
- **Header preservation**: Maintains column headers across chunks for context
- **Chart extraction**: Preserves visual elements and formatting

**Basic Excel Processing**::

    from rhubarb import DocAnalysis
    import boto3

    # Process an Excel file
    da = DocAnalysis(
        file_path="financial_report.xlsx", 
        boto3_session=boto3.Session()
    )
    
    response = da.run(message="What are the total sales figures?")
    print(response.content)

**Large Spreadsheet Handling**:

For spreadsheets with more than 1000 rows, Rhubarb automatically:

1. **Creates header section**: First 5 rows preserved as context
2. **Chunks data**: Breaks remaining data into 100-row sections
3. **Limits processing**: Maximum 10 chunks (plus headers) to respect 20-page limit
4. **Maintains context**: Each chunk includes headers for reference

PowerPoint Support (.pptx)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Process PowerPoint presentations slide by slide:

- **Slide-by-slide processing**: Each slide becomes a separate "page"
- **Text extraction**: Captures all text content from slides
- **Layout preservation**: Maintains visual structure and formatting
- **Image placeholders**: Identifies and marks embedded images
- **Speaker notes**: Optional extraction of presenter notes with visual separation

**Basic PowerPoint Processing**::

    from rhubarb import DocAnalysis
    import boto3

    # Process a PowerPoint presentation
    da = DocAnalysis(
        file_path="company_presentation.pptx", 
        boto3_session=boto3.Session()
    )
    
    # Analyze specific slides
    response = da.run(
        message="Summarize the key points from the presentation",
        pages=[1, 2, 3]  # Process first 3 slides
    )

**Including Speaker Notes**::

    # Process PowerPoint with speaker notes included
    da_with_notes = DocAnalysis(
        file_path="presentation_with_notes.pptx", 
        include_powerpoint_notes=True,  # Include speaker notes
        boto3_session=boto3.Session()
    )
    
    response = da_with_notes.run(
        message="Analyze both slide content and speaker notes. What additional context do the notes provide?"
    )

When ``include_powerpoint_notes=True``, Rhubarb will:

- Extract speaker notes from each slide's notes section
- Visually separate notes from slide content with a dashed line
- Display notes with "Speaker Notes:" label and yellow highlighting
- Limit notes text to 400 characters to prevent image overflow
- Gracefully handle slides without notes or extraction failures

Word Document Support (.docx)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enhanced Word document processing (existing feature):

- **Paragraph-based processing**: Each paragraph treated as a page unit
- **Text extraction**: Full text content with formatting preserved
- **Image handling**: Embedded images processed appropriately

Usage Examples
--------------

Processing Multiple Office Formats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    import boto3
    from rhubarb import DocAnalysis

    session = boto3.Session()

    # Process Excel file
    excel_analysis = DocAnalysis(
        file_path="budget_2024.xlsx",
        boto3_session=session
    )
    
    excel_response = excel_analysis.run(
        message="What are the key budget allocations?"
    )

    # Process PowerPoint file  
    ppt_analysis = DocAnalysis(
        file_path="quarterly_review.pptx",
        boto3_session=session
    )
    
    ppt_response = ppt_analysis.run(
        message="What were the main achievements this quarter?"
    )

S3 Integration
~~~~~~~~~~~~~

Office formats work seamlessly with S3 storage::

    # Process Office files stored in S3
    da = DocAnalysis(
        file_path="s3://my-bucket/reports/annual_report.xlsx",
        boto3_session=boto3.Session()
    )
    
    response = da.run(message="Extract key financial metrics")

Large Document Processing
~~~~~~~~~~~~~~~~~~~~~~~~

Office formats integrate with Rhubarb's sliding window approach::

    # Large Excel file with sliding window
    da = DocAnalysis(
        file_path="massive_dataset.xlsx",
        sliding_window_overlap=2,  # 2-page overlap between chunks
        boto3_session=boto3.Session()
    )
    
    response = da.run(message="Analyze trends in the data")

Page Selection
~~~~~~~~~~~~~

Control which parts of Office documents to process::

    # Process specific worksheets/slides
    da = DocAnalysis(
        file_path="complex_workbook.xlsx",
        pages=[1, 3, 5],  # Process worksheets 1, 3, and 5
        boto3_session=boto3.Session()
    )
    
    # Process all content (up to 20 pages)
    da_all = DocAnalysis(
        file_path="presentation.pptx",
        pages=[0],  # Process all slides
        boto3_session=boto3.Session()
    )

Performance Considerations
-------------------------

Memory Management
~~~~~~~~~~~~~~~~

- **Read-only processing**: Excel files loaded in read-only mode for efficiency
- **Streaming approach**: Large files processed in chunks to manage memory
- **Automatic cleanup**: Temporary resources cleaned up after processing

Large File Handling
~~~~~~~~~~~~~~~~~~

- **Excel files >1000 rows**: Automatically chunked into sections
- **PowerPoint files >20 slides**: Respects 20-page processing limit
- **Memory monitoring**: Efficient processing of large Office documents

Visual Quality
~~~~~~~~~~~~~

- **150 DPI rendering**: High-quality PNG conversion matching PDF processing
- **Formatting preservation**: Maintains colors, fonts, and layout
- **Chart handling**: Embedded charts converted to visual representations

Error Handling
--------------

Common issues and solutions:

**File Format Issues**::

    try:
        da = DocAnalysis(
            file_path="document.xlsx",
            boto3_session=session
        )
        response = da.run(message="Analyze the data")
    except ValueError as e:
        if "Unsupported file type" in str(e):
            print("File format not supported")
    except RuntimeError as e:
        print(f"Processing error: {e}")

**Large File Handling**::

    # For very large Excel files, consider processing specific sheets
    da = DocAnalysis(
        file_path="huge_spreadsheet.xlsx",
        pages=[1, 2],  # Process only first two worksheets
        boto3_session=session
    )

Best Practices
--------------

1. **File Size Management**: For very large Excel files, consider processing specific worksheets rather than the entire workbook
2. **Memory Efficiency**: Use page selection to limit processing scope when appropriate
3. **S3 Integration**: Store large Office files in S3 for better performance and scalability
4. **Error Handling**: Implement proper error handling for file format and processing issues
5. **Content Optimization**: Large spreadsheets are automatically optimized for AI processing through intelligent chunking

Integration with Existing Features
---------------------------------

Office format support integrates seamlessly with all existing Rhubarb features:

- **Structured Data Extraction**: Use JSON schemas with Office documents
- **Named Entity Recognition**: Extract entities from spreadsheets and presentations  
- **Document Classification**: Classify Office documents using vector similarity
- **Streaming Responses**: Get real-time responses for Office document analysis
- **Cost Tracking**: Monitor token usage for Office document processing

The Office format support maintains the same simple API while providing powerful document understanding capabilities for modern business workflows.
