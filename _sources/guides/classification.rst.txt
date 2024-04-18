Document Classification
=======================

You can perform a more accurate, and cost effective document classification with Rhubarb's vector sampling functionality. Internally, Rhubarb uses Amazon Titan Multi-modal embedding model for this purpose. Here are the high level steps you will follow to setup a classifier, and then run document classifications with it.

How are the documents classified?
---------------------------------

The premise of classification based on vector sampling relies on the fact that you have a small set of labeled documents and 
their corresponding vectors (embeddings). Given this sample set, you can generate vector embeddings of a new document and 
perform similarity check with your sample set to determine which type of document the new document closely resembles to. 

For that, Rhubarb offers two methods of choice- 

1. **Cosine Similarity** (`cosine`) to measure the similarity of a new document's vector embeddings with the sample set of labeled vectors. Cosine Similarity measures the cosine of the angle between two non-zero vectors in a multi-dimensional space. It's derived from the dot product of the vectors divided by the product of their magnitudes (norms). For each class, it finds the maximum similarity score among all its vectors compared to the page's embedding. This score represents how closely the page's content resembles the content typical of that class. If the highest similarity score across all classes is below a certain threshold (unknown_threshold), it classifies the page as "UNKNOWN". This means that the page does not closely resemble any of the known classes above the specified confidence level. The UNKNOWN class is assigned the highest similarity score found, even though it's below the threshold (more on this later).
2. **Euclidean distance**, also known as L2 distance (`l2`), measures the straight line distance between two points in a multi-dimensional space. It is derived from the square root of the sum of the squared differences between corresponding elements of the two vectors. For each class, the Euclidean distance between the page's embedding and each of the class's sample vectors is calculated. Unlike cosine similarity, which measures the angle between vectors, Euclidean distance measures the magnitude of difference between vectors. A smaller Euclidean distance indicates a closer or more similar match between the vectors. Therefore, for each class, you would typically look for the minimum Euclidean distance between the page's embedding and the class's vectors to determine the closest match.


Pre-requisites
--------------

1. You will need to define a the classes (a.k.a. labels or document class) for the documents. 
2. Collect a few sample documents for each class (minimum 1 sample max 10 samples each class)
3. Create a CSV manifest file
4. Run sampling using the manifest file, capture the :code:`sample ID` (you will need this to run classification)
5. Run classifications with new document using the :code:`sample ID` from step 4.


Create a manifest file
----------------------

Your manifest file should be of CSV format. For example

.. code-block:: text

    BANK_STATEMENT,s3://your-bucket/samples/bank_stmt_0.pdf,1
    BANK_STATEMENT,s3://your-bucket/samples/bank_stmt_1.pdf,1
    BANK_STATEMENT,s3://your-bucket/samples/bank_stmt_2.pdf,1
    INVOICE,s3://your-bucket/samples/invoice_0.pdf,1
    INVOICE,s3://your-bucket/samples/invoice_1.pdf,1
    RECEIPT,s3://your-bucket/samples/receipt_0.pdf,1
    RECEIPT,s3://your-bucket/samples/receipt_1.pdf,1
    RECEIPT,s3://your-bucket/samples/receipt_2.pdf,1


The manifest CSV file must contain three fields-

1. The class label should be the first field
2. The sample document belonging to that class, either local path or :code:`s3://` location of the sample document. S3 locations are recommended but local path's can be used during development.
3. Third column is the page number of the document (in case the document is multi-page pdf)

.. note:: If you would like to include all pages of a multi-page document in the sample dataset then you must make separate lines in the csv with the same document and the subsequent page number.

You can store this manifest file into an S3 location (recommended) or use it locally. Once you have your manifest file ready we can create a classifier.

Setup a classifier
------------------

You initialize an instance of :code:`DocClassification` and call the :code:`run_sampling()` function with the manifest file path to start the sampling process. This should be a fairly quick process and shouldn't take more than a few minutes. 
The function will return a :code:`sample_id` which you can subsequently use to run document classification tasks. You will also need to provide an S3 bucket where the resulting vector samples will be stored for later use.

.. code:: python

    from rhubarb import DocClassification
    import boto3

    session = boto3.Session()

    dc = DocClassification(bucket_name="your-classifier-bucket", boto3_session=session)
    classifier = dc.run_sampling(manifest_path="s3://your-bucket/manifest.csv")

Sample output

.. code-block:: json

    {
        "sample_id": "rb_classifier_1711608335"
    }

Creating a classifier (sample) is a one-time process, i.e. once you setup your classifier you can use the `sample_id` to perform document classification tasks.

Using a classifier
------------------

You use the :code:`run_classify()` function with path to the new document you would like to classify. The file can be a multi-page document and Rhubarb will classify each page individually.

.. code:: python

    from rhubarb import DocClassification
    import boto3

    session = boto3.Session()

    dc = DocClassification(bucket_name="your-classifier-bucket", boto3_session=session)
    results = dc.run_classify(sample_id="rb_classifier_1711608335", 
                              file_path="./test_docs/bank_stmt.pdf")

Sample output

.. code-block:: json

    [
        {
            "page": 1, 
            "classification": [
                    {
                        "class": "BANK_STATEMENT", 
                        "score": 0.92
                    }
                ]
        }
    ]

Using :code:`unknown_threshold` 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some cases, your document processing pipeline may encounter documents that do not belong to any of the pre-configured classes. 
In such cases, it can be useful to mark these documents as :code:`UNKNOWN` and isolate them for further analysis. This can be achieved 
using the :code:`unknown_threshold` parameter. By default, the value is set to :code:`0.8` i.e. any document below this threshold is 
automatically marked as :code:`UNKNOWN`. However, you can override this value to further tune your classification task.

.. code:: python
   :emphasize-lines: 8,9

    from rhubarb import DocClassification
    import boto3

    session = boto3.Session()
    dc = DocClassification(bucket_name="your-classifier-bucket", boto3_session=session)
    results = dc.run_classify(sample_id="rb_classifier_1711608335", 
                            file_path="./test_docs/Sample1.pdf", 
                            top_n=2,
                            unknown_threshold=0.85)
    results

Sample output

.. code-block:: json

   [
       {
           "page": 1,
           "classification": [
               {"class": "BANK_STATEMENT", "score": 0.93},
               {"class": "DISCHARGE_SUMMARY", "score": 0.76}
           ]
       },
       {
           "page": 2,
           "classification": [
               {"class": "RECEIPT", "score": 1.0},
               {"class": "INVOICE", "score": 0.78}
           ]
       },
       {"page": 3, "classification": [{"class": "UNKNOWN", "score": 0.6150004682895025}]},
       {"page": 4, "classification": [{"class": "UNKNOWN", "score": 0.7916701829486292}]},
       {"page": 5, "classification": [{"class": "UNKNOWN", "score": 0.8255265125891919}]},
       {"page": 6, "classification": [{"class": "UNKNOWN", "score": 0.768307452125929}]}
   ]


The score for :code:`UNKNOWN` classification is the highest similarity score (even if it's below the threshold). This gives a sense of 
how close the document was to being classified into one of the known classes before being deemed unknown. To view what the unknown 
pages is actually getting classified into, you can reduce the :code:`unknown_threshold` and re-run the classification. Ideally, you 
would experiment and tune this score based on your use cases, the number of samples you used while creating the classifier, the 
number of classes, and the different type of documents you receive for your use-case.

Using :code:`similarity_metric`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default Rhubarb uses *Cosine similarity* to determine the class of a given page. If default Cosine similarity is used then 
scores can be between 0 and 1, and the higher the score the better. Higher number means the given document is most similar to 
the samples in the given class. 

However, you can also choose *Euclidian distance* similarity metric (a.k.a L2 distance). In this case, scores will range beween 
0 and 1, and the lower the number, the better, which means the straight line distance between the vector of the give document 
and the vector's of the class it is categorized in is the least. You can set the :code:`similarity_metric` to :code:`l2` to force using 
Euclidian distance for classification.

.. note:: In case of Euclidian distance, your :code:`unknown_threshold` is the inverse of :code:`cosine` similarity. Which means if :code:`unknown_threshold` is set to :code:`0.5` then any class with score more than :code:`0.5` will be marked as :code:`UNKNOWN` since it is the most dissimilar to all the known classes.

.. code:: python
   :emphasize-lines: 8,9

   from rhubarb import DocClassification
   import boto3

   session = boto3.Session()
   dc = DocClassification(bucket_name="your-classifier-bucket", boto3_session=session)
   results = dc.run_classify(sample_id="rb_classifier_1711608335", 
                             file_path="./test_docs/Sample1.pdf", 
                             similarity_metric="l2",
                             unknown_threshold=0.5) # threshold is low because smaller is better

Sample output

.. code-block:: json

   [
       {"page": 1, "classification": [{"class": "BANK_STATEMENT", "score": 0.38}]},
       {"page": 2, "classification": [{"class": "RECEIPT", "score": 0.0}]},
       {"page": 3, "classification": [{"class": "UNKNOWN", "score": 0.87749589194715}]},
       {"page": 4, "classification": [{"class": "UNKNOWN", "score": 0.6454917724396393}]},
       {"page": 5, "classification": [{"class": "UNKNOWN", "score": 0.5907173241851739}]},
       {"page": 6, "classification": [{"class": "UNKNOWN", "score": 0.6807239544254996}]}
   ]



Viewing a classifier
--------------------

You can view the details of an existing classifier using the :code:`view_sample()` function. This will show you the classes you 
have configured for your classifiers and the samples you used while creating the classifier.

.. code:: python
   :emphasize-lines: 7

   from rhubarb import DocClassification
   import boto3

   session = boto3.Session()

   dc = DocClassification(bucket_name="your-classifier-bucket", boto3_session=session)
   dc.view_sample(sample_id="rb_classifier_1711608335")

Sample output

.. code-block:: json

   [
       {"class": "BANK_STATEMENT", "num_samples": 6},
       {"class": "INVOICE", "num_samples": 6},
       {"class": "RECEIPT", "num_samples": 6}
   ]


Updating a classifier
---------------------

You may have a need to subsequently update your classifier to add new classes, or samples. You can easily do that just like 
creating a new classifier with the help of a new manifest CSV file. But this time, you will need to supply an existing 
:code:`sample_id` to the :code:`run_sampling()` function via the :code:`update_sample_id` parameter. This will process the 
manifest file but instead of creating a new classifier, will update the existing classifier (sample). For example with our new 
:code:`manifest2.csv` we would like to update our existing sample.

:code:`manifest2.csv`

.. code-block:: text

   DISCHARGE_SUMMARY,s3://your-bucket/samples/discharge_summary_0.pdf,1
   DISCHARGE_SUMMARY,s3://your-bucket/samples/discharge_summary_1.pdf,1
   DISCHARGE_SUMMARY,s3://your-bucket/samples/discharge_summary_2.pdf,1
   DISCHARGE_SUMMARY,s3://your-bucket/samples/discharge_summary_3.pdf,1
   DISCHARGE_SUMMARY,s3://your-bucket/samples/discharge_summary_4.pdf,1


.. note:: It is recommended that you use samples that were not used before while creating the classifier (sample), since Rhubarb doesn't do any de-duplication internally.

.. code:: python
   :emphasize-lines: 8

    from rhubarb import DocClassification
    import boto3

    session = boto3.Session()
    dc = DocClassification(bucket_name="your-classifier-bucket", 
                           boto3_session=session)
    classifier = dc.run_sampling(manifest_path="s3://your-bucket/manifest2.csv", 
                                 update_sample_id="rb_classifier_1711608335")



Sample output

.. code-block:: json

   {
      "sample_id": "rb_classifier_1711608335"
   }

View the updated classifier

.. code:: python

   from rhubarb import DocClassification
   import boto3

   session = boto3.Session()

   dc = DocClassification(bucket_name="your-classifier-bucket", boto3_session=session)
   dc.view_sample(sample_id="rb_classifier_1711608335")

Sample output

.. code-block:: json

   [
       {"class": "BANK_STATEMENT", "num_samples": 6},
       {"class": "INVOICE", "num_samples": 6},
       {"class": "RECEIPT", "num_samples": 6},
       {"class": "DISCHARGE_SUMMARY", "num_samples": 5}
   ]



How is the classifier stored?
-----------------------------

Your classifier will contain three distinct parts

1. A unique identifier (:code:`sample_id`)
2. The class labels (i.e. :code:`BANK_STATEMENT`, :code:`RECEIPTS` and so on)
3. The multi-modal vector embeddings for each of the sample document for each class as specified in the manifest file.

All of this data is arranged and stored in a compressed Parquet file in the S3 bucket you provide (via the :code:`bucket_name` 
parameter). Within the bucket, Rhubarb will store all your classifiers under the prefix :code:`rb_classification` by default. 
However, you can override this prefix via Rhubarb's :code:`GlobalConfig` and overriding :code:`classification_prefix` config 
using the :code:`update_config()` function, with your desired prefix.

.. note:: See `Organizing S3 objects using prefixes <https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-prefixes.html>`_

.. warning:: The prefix must not contain any leading or trailing :code:`/`.

.. code:: python
   :emphasize-lines: 6

      from rhubarb import DocClassification, GlobalConfig
      import boto3

      session = boto3.Session()

      GlobalConfig.update_config(classification_prefix="my_classifiers")
      dc = DocClassification(bucket_name="your-classifier-bucket", boto3_session=session)
      classifier = dc.run_sampling(manifest_path="s3://your-bucket/manifest.csv")