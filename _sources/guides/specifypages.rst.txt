Specify Document Pages
======================

By default, Rhubarb attempts to process all pages (up to 20 pages) of a PDF or TIFF file. However, you can specify page numbers
to process by passing in :code:`pages` parameter to :code:`DocAnalysis`.

.. note:: Acceptable page numbers for :code:`pages` starts with 1, and max 20.

Specify a single page
---------------------

Specify a single page by passing an array of page number, for example to process the third page of a document

.. code:: python
   :emphasize-lines: 5

     from rhubarb import DocAnalysis

     da = DocAnalysis(file_path="./test_docs/employee_enrollment.pdf", 
                      boto3_session=session,
                      pages=[3])
     resp = da.run(message="For beneficiary type 'Secondary', what is the full name?")

Specify multiple pages
----------------------

Specify multiple pages by passing an array of page numbers, for example to process the 3rd, 5th, and 6th page of a document

.. code:: python
   :emphasize-lines: 5
   
     from rhubarb import DocAnalysis

     da = DocAnalysis(file_path="./test_docs/employee_enrollment.pdf", 
                      boto3_session=session,
                      pages=[3, 5, 6])
     resp = da.run(message="For beneficiary type 'Secondary', what is the full name?")
