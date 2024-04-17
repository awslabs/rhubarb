# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import io
import logging
from typing import Any, Dict, List, Literal
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pyarrow.parquet as pq
from pydantic import Field, BaseModel, StrictInt, PrivateAttr, StrictFloat, model_validator
from botocore.config import Config

from rhubarb.config import GlobalConfig
from rhubarb.invocations import Invocations
from rhubarb.file_converter import FileConverter

logger = logging.getLogger(__name__)

class Classification(BaseModel):

    classifier_id: str = Field(None, description="The sampler or classifier ID.")
    """The sampler or classifier ID"""

    file_path: str = Field(None, description="The path of the file that needs to be classified.")
    """The path of the file that needs to be classified."""

    modelID: str
    """The embedding model ID in Bedrock"""

    similarity_metric: Literal["cosine", "l2"] = "cosine"
    """The similarity mechanism to use"""

    top_n: StrictInt = Field(default=1, ge=0, lt=4, description="Top n classes to return")
    """Top n classes to return"""

    unknown_threshold: StrictFloat = Field(default=0.8, ge=0, lt=1.0, description="The threshold to label a page UNKNOWN")
    """The threshold to label a page UNKNOWN"""

    pages: List[int] = Field(default=[0])
    """Pages of a multi-page PDF or TIF to process
    - [0] will process all pages upto 20 pages max
    - [1,3,5] will process pages 1, 3 and 5
    """

    bucket_name: str = Field(None, description="The name of the S3 bucket where sample resides.")
    """Output location where samples will be stored"""

    boto3_session: Any
    """Instance of boto3.session.Session"""

    _s3_client: Any = PrivateAttr(default=None)
    """boto3 s3 client, will get overriten by boto3_session"""

    _bedrock_client: Any = PrivateAttr(default=None)
    """boto3 bedrock-runtime client, will get overriten by boto3_session"""

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, values: dict) -> dict:        
        classifier_id = values.get('classifier_id')
        file_path = values.get('file_path')
        pages = values.get("pages", [0])
        bucket_name = values.get("bucket_name")

        if 0 in pages and len(pages) > 1:
            logger.error("If specific pages are provided, page number 0 is invalid.")
            raise ValueError(
                "If specific pages are provided, page number 0 is invalid. Must be 1 or greater."
            )
        # validate the file path
        blocked_schemes = ["http://", "https://", "ftp://"]
        if any(file_path.startswith(scheme) for scheme in blocked_schemes):
            logger.error("file_path must be a local file system path or an s3:// path")
            raise ValueError(
                "file_path must be a local file system path or an s3:// path"
            )
        
        s3_config = Config(retries={"max_attempts": 0, "mode": "standard"}, signature_version="s3v4")
        br_config = Config(retries={"max_attempts": 0, "mode": "standard"})
        session = values.get("boto3_session")
        cls._s3_client = session.client("s3", config=s3_config)
        cls._bedrock_client = session.client("bedrock-runtime", config=br_config)

        # validate the classifier/sample ID
        try:
            config = GlobalConfig.get_instance()
            key = f"{config.classification_prefix}/{classifier_id}/{classifier_id}.parquet"
            cls._s3_client.head_object(Bucket=bucket_name, 
                                       Key=key)            
        except cls._s3_client.exceptions.ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                logger.error("Classifier file does not exist. Check the S3 bucket or create a new classifier.")
                raise ValueError("Classifier file does not exist. Check the S3 bucket or create a new classifier.")
            else:
                logger.error(f"Error checking for Parquet file: {str(e)}")
                raise e
        return values
    
    
    def _convert_to_base64(self, pages: List[int]) -> List[Dict[str, Any]]:
        """
        Converts page images to Base64 strings

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the base64 string of pages.
        """
        converter = FileConverter(file_path=self.file_path, 
                                  pages=pages, 
                                  s3_client=self._s3_client)
        return converter.convert_to_base64()
    
    def _gen_embedding(self, body: Any) -> List[Any]:
        """
        Bedrock Embdedding model API call

        Returns:
            List[Any]: An embedding vector.
        """
        model_invoke = Invocations(body=body,
                                   bedrock_client=self._bedrock_client,
                                   model_id=self.modelID)
        return model_invoke.invoke_embedding()
    
    def _gen_embeddings_for_pages(self, base64_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Bulk Bedrock Embdedding model API call for all classes and their samples

        Returns:
            None
        """
        max_workers = 10        
        page_embeddings = []
        errors = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self._gen_embedding, {
                "inputImage": k["base64string"],
                "embeddingConfig": {"outputEmbeddingLength": 256}
            }): k["page"] for k in base64_list}
            for future in as_completed(futures):
                page_num = futures[future]
                try:
                    embedding = future.result()
                    page_embeddings.append({ "page": page_num, "embedding": embedding })
                except Exception as e:                    
                    error_message = f"Error processing page: {page_num}: {str(e)}"
                    logger.error(error_message)
                    errors.append({"page": page_num, "error": error_message})
        return page_embeddings, errors
    
    def _get_sample_embeddings(self) -> dict:
        config = GlobalConfig.get_instance()
        file_key=f"{config.classification_prefix}/{self.classifier_id}/{self.classifier_id}.parquet"
        try:            
            obj = self._s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            body = obj['Body'].read()
            bytes_io = io.BytesIO(body)
            table = pq.read_table(bytes_io)

            classes = table['class']
            vectors = table['vector']

            samples = {}
            for i in range(len(classes)):
                class_name = classes[i].as_py()
                vector = vectors[i].as_py()

                if class_name not in samples:
                    samples[class_name] = []
                samples[class_name].append(vector)
            return samples
        except Exception as e:
            logger.error(f"Error reading classifier sample: {str(e)}")
            raise e
    
    def _euclidian_distance(self,
                            page_vector: Dict[str, Any],
                            class_vectors: Dict[str, List[List[float]]]) -> Dict[str, Any]:
        """
        Classifies a page based on the embedding vector's Euclidian distance to vectors of known classes.
        
        Args:
            embedding_data (Dict[str, Any]): Embedding data containing page number and vector.
            class_vectors (Dict[str, List[List[float]]]): Known classes and their corresponding vectors.
            top_n (int, optional): Number of top similar classes to return. Defaults to 1.
        
        Returns:
            Dict[str, Any]: The page number with class and the euclidian distance as score.
        """
        page = page_vector["page"]
        page_embedding = np.array(page_vector["embedding"])
        category_scores = []

        for class_label, embeddings in class_vectors.items():            
            distances = [
                np.linalg.norm(page_embedding - np.array(vec))
                for vec in embeddings
            ]
            if distances:
                # Use minimum distance instead of maximum similarity
                min_distance = min(distances)
                category_scores.append((class_label, min_distance))

        if category_scores and min(category_scores, key=lambda x: x[1])[1] > self.unknown_threshold:
            result = {
                "page": page,
                "classification": [{"class": "UNKNOWN", "score": min(category_scores, key=lambda x: x[1])[1]}]  # Use the minimum distance score as UNKNOWN score
            }
        else:
            top_classes = sorted(category_scores, key=lambda x: x[1])[:self.top_n]        

            result ={
                "page": page,
                "classification": [{"class": class_label, "score": round(score, 2)} for class_label, score in top_classes]
            }
        return result

    def _cosine_similarity(self,
                           page_vector: Dict[str, Any],
                           class_vectors: Dict[str, List[List[float]]]) -> Dict[str, Any]:
        """
        Classifies a page based on the embedding vector's cosine similarity to vectors of known classes.
        
        Args:
            embedding_data (Dict[str, Any]): Embedding data containing page number and vector.
            class_vectors (Dict[str, List[List[float]]]): Known classes and their corresponding vectors.
            top_n (int, optional): Number of top similar classes to return. Defaults to 1.
        
        Returns:
            Dict[str, Any]: The page number with class and the cosine similarity as score.
        """
        page = page_vector["page"]
        page_embedding = np.array(page_vector["embedding"])
        category_scores = []
        for class_label, embeddings in class_vectors.items():
            similarities = [
                np.dot(page_embedding, np.array(vec)) / (np.linalg.norm(page_embedding) * np.linalg.norm(vec))
                for vec in embeddings
            ]
            if similarities:
                max_similarity = max(similarities)
                category_scores.append((class_label, max_similarity))

        if category_scores and max(category_scores, key=lambda x: x[1])[1] < self.unknown_threshold:
            result = {
                "page": page,
                "classification": [{"class": "UNKNOWN", "score": max(category_scores, key=lambda x: x[1])[1]}]  # Use highest similarity score as UNKNOWN score
            }
        else:
            top_classes = sorted(category_scores, key=lambda x: x[1], reverse=True)[:self.top_n]        

            result ={
                "page": page,
                "classification": [{"class": class_label, "score": round(score, 2)} for class_label, score in top_classes]
            }
        return result

    def classify_doc(self) -> dict:
        base64_list = self._convert_to_base64(pages=self.pages)
        page_embeddings, errors = self._gen_embeddings_for_pages(base64_list=base64_list)
        samples = self._get_sample_embeddings()

        results = []
        for page in page_embeddings:
            if self.similarity_metric == "cosine":
                result = self._cosine_similarity(page_vector=page, class_vectors=samples)
            elif self.similarity_metric == "l2":
                result = self._euclidian_distance(page_vector=page, class_vectors=samples)
            results.append(result)                
        sorted_results = sorted(results, key=lambda x: x["page"])
        return sorted_results