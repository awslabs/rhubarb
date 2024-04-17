# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import re
import csv
import logging
from io import StringIO
from typing import Any, Dict, List, Tuple, Optional

from pydantic import Field, BaseModel, PrivateAttr, model_validator
from botocore.config import Config

from rhubarb.models import EmbeddingModels
from rhubarb.classification import VectorSampler, Classification

logger = logging.getLogger(__name__)

class DocClassification(BaseModel):
    """A class to setup and perform document classification using Multi-modal embedding models."""

    bucket_name: str = Field(None, description="The name of the S3 bucket for storing sample vectors.")
    """Output location where samples will be stored"""

    modelId: EmbeddingModels = Field(default=EmbeddingModels.TITAN_EMBED_MM_V1)
    """Bedrock Embedding Model ID"""

    boto3_session: Any
    """Instance of boto3.session.Session"""

    _s3_client: Any = PrivateAttr(default=None)
    """boto3 s3 client, will get overriten by boto3_session"""

    _bedrock_client: Any = PrivateAttr(default=None)
    """boto3 bedrock-runtime client, will get overriten by boto3_session"""

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, values: dict) -> dict:        
        s3_config = Config(retries={"max_attempts": 0, "mode": "standard"}, signature_version="s3v4")
        br_config = Config(retries={"max_attempts": 0, "mode": "standard"})
        session = values.get("boto3_session")
        cls._s3_client = session.client("s3", config=s3_config)
        cls._bedrock_client = session.client("bedrock-runtime", config=br_config)

        return values
    
    def _parse_s3_path(self, s3_path: str) -> tuple[str, str]:
        """
        Parse the S3 file path and extract the bucket name and key.

        Args:
            s3_path (str): The S3 file path.

        Returns:
            tuple[str, str]: A tuple containing the bucket name and key.
        """
        parts = s3_path[5:].partition("/")
        bucket_name = parts[0]
        key = parts[2]
        return bucket_name, key

    def _validate_manifest(self, manifest_path: str) -> Dict[str, List[Tuple[str, int]]]:
        """
        Validate the CSV file based on the following criteria:
        1. It contains 2 columns
        2. The first column contains only alphabets, numbers, or underscores (_)
        3. The second column is a local or s3:// path

        Args:
            - `manifest_path` (`str`): The manifest file path (local or S3)
        """
        blocked_schemes = ["http://", "https://", "ftp://"]
        if any(manifest_path.startswith(scheme) for scheme in blocked_schemes):
            logger.error("manifest_path must be a local file system path or an s3:// path")
            raise ValueError(
                "manifest_path must be a local file system path or an s3:// path"
            )
        data: Dict[str, List[Tuple[str, int]]] = {}
        try:
            if manifest_path.startswith('s3://'):
                bucket, key = self._parse_s3_path(s3_path=manifest_path)
                response = self._s3_client.get_object(Bucket=bucket, Key=key)
                file_content = StringIO(response['Body'].read().decode('utf-8'))
            # Otherwise, assume it's a local file system path
            else:
                file_content = open(manifest_path, 'r')

            with file_content as content:
                reader = csv.reader(content, delimiter=',')
                for row in reader:
                    if len(row) != 3:
                        raise ValueError(
                            "Manifest CSV file should contain exactly 3 columns."
                        )

                    label, file_path, count = row
                    if not re.match(r'^[a-zA-Z0-9_]+$', label):
                        raise ValueError("Class names should contain only alphabets, numbers, or underscores.")

                    if not file_path.startswith('s3://') and not file_path.startswith('./'):
                        raise ValueError("File paths cab be a local or s3:// path.")
                    
                    try:
                        count = int(count)
                    except ValueError:
                        raise ValueError("Page number value should be a number.")
                    
                    if count == 0:
                        raise ValueError("Page number cannot be zero.")
                    
                    if label in data:
                        data[label].append((file_path, count))
                    else:
                        data[label] = [(file_path, count)]
        except Exception as e:
            raise e
        return data

    def run_sampling(self, manifest_path: str, update_sample_id: Optional[str] = None) -> Dict[str, str]:
        """
        Creates vector samples of the provided files in the manifest CSV. If a sample ID
        is passed then it will be updated, else a new one will be created

        Args:
            - `update_sample_id` (`Optional[str]`): The sample ID to update.
        """ 
        try:
            manifest_data = self._validate_manifest(manifest_path=manifest_path)
            sampler = VectorSampler(bucket_name=self.bucket_name,
                                    bedrock_client=self._bedrock_client,
                                    s3_client=self._s3_client,
                                    modelID=self.modelId.value)
            sample_id = sampler.run_sampler(manifest_data=manifest_data, 
                                                update_classifier=update_sample_id)
            return {
                "sample_id": sample_id
            }
        except Exception as e:
            raise e

    def view_sample(self, sample_id: str) -> List[Dict[str, Any]]:
        """
        View details of a classification sample set including the classes and the number
        of samples per class

        Args:
            - `sample_id` (`str`): The sample ID to view.
        """ 
        try:
            sampler = VectorSampler(bucket_name=self.bucket_name,
                                    bedrock_client=self._bedrock_client,
                                    s3_client=self._s3_client,
                                    modelID=self.modelId.value)
            sample = sampler.view_classifier(classifier_id=sample_id)
            return sample
        except Exception as e:
            raise e

    def run_classify(self, 
                     sample_id: str, 
                     file_path: str, 
                     pages: Optional[List[int]] = [0], 
                     similarity_metric: Optional[str] = "cosine",
                     top_n: Optional[int] = 1,
                     unknown_threshold: Optional[float] = 0.8) -> dict:
        """
        Given a sample/classifier ID classifies a document and its pages
        to different classes

        Args:
            - `sample_id` (`str`): The sample ID to use.
            - `file_path` (`str`): The local or `s3://` path of the document to classify
            - `pages` (Optional(`list`)): Optional. List of page numbers to classify.
               defaults to `[0]` which means all pages upto a maximum of 20 pages per document.
            - `similarity_metric` (Optional(`str`)): Similarity Metric to use. Defaults to 
              `cosine`. Possible `l2` or `cosine`.
            - `top_n` (Optional(`int`)): Optional. Number of top classes to return (per page). 
               defaults to 1.
            - `unknown_threshold` (Optional(`float`)): The threshold to label a page UNKNOWN. 
               defaults to 0.8
        """ 
        try:
            classify = Classification(classifier_id=sample_id,
                                      file_path=file_path,
                                      pages=pages,
                                      similarity_metric=similarity_metric,
                                      top_n = top_n,
                                      unknown_threshold=unknown_threshold,
                                      bucket_name = self.bucket_name,
                                      modelID = self.modelId,
                                      boto3_session = self.boto3_session)
            result = classify.classify_doc()
            return result
        except Exception as e:
            raise e

    