# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import io
import os
import json
import time
import shutil
import logging
import platform
import tempfile
from typing import Any, Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from rhubarb.config import GlobalConfig
from rhubarb.invocations import Invocations
from rhubarb.file_converter import FileConverter

logger = logging.getLogger(__name__)

class VectorSampler:
    # This is S3 specific Sampling storage
    def __init__(self,
                 bucket_name: str,
                 bedrock_client: Any,
                 s3_client: Any,
                 modelID: str) -> None:
        self.bedrock_client = bedrock_client
        self.s3_client = s3_client
        self.modelID = modelID
        self.bucket_name = bucket_name
        self.config = GlobalConfig.get_instance()
        self.classifier_id = self._generate_unique_id()
        if platform.system() == 'Windows':
            with tempfile.TemporaryDirectory() as temp_dir:
                self.cache_dir=temp_dir
        else:
            with tempfile.TemporaryDirectory(dir='/tmp') as temp_dir:
                self.cache_dir=temp_dir

    def _save_to_s3(self, json_data: dict, file_name: str) -> None:
        """
        Writes the given JSON data to an S3 file.

        Parameters:
        - json_data (dict): The JSON data to be written.
        - file_name (str): The name of the file to be created in S3.
        """        
        try:
            json_string = json.dumps(json_data)
            self.s3_client.put_object(Bucket = self.bucket_name,
                                      Key = f"{self.config.classification_prefix}/{self.classifier_id}/{file_name}",
                                      Body = json_string)
        except Exception as e:            
            logger.error(f"Error: {str(e)}")
            raise e
        
    def _upload_to_s3(self, file_path: str, s3_key: str) -> None:
        """
        Uploads a file to an S3 bucket.

        :param file_path: Local path to the file to upload.
        :param s3_key: The S3 key (path) where the file will be stored.
        """
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
        except Exception as e:
            logger.error(f"Failed to upload {file_path} to S3: {str(e)}")
            raise e

    def _check_valid_classifier(self, object_path: str) -> bool:
        """
        Checks if the provided classifier exists in S3 in case existing classifier
        is being updated with new samples.

        Returns:
            bool: True if Classifier exists

        Raises:
            Exception: ValueError if classifier is not found
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, 
                                       Key=object_path)
            return True 
        except self.s3_client.exceptions.ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                logger.error("Classifier file does not exist. Check the S3 bucket or create a new classifier.")
                raise ValueError("Classifier file does not exist. Check the S3 bucket or create a new classifier.")
            else:
                logger.error(f"Error checking for Parquet file: {str(e)}")
                raise e

    def _generate_unique_id(self) -> str:
        """
        Generates a unique classifier ID

        Returns:
            str: A unique classifier ID of the format `rb_classifier_XXXXXXX`
        """
        prefix = "rb_classifier_"
        timestamp = int(time.time())
        unique_id = f"{prefix}{timestamp}"
        return unique_id
    
    def _embeddings_to_pq(self, data: dict, update: bool) -> None:
        """
        Process the JSON containing vectors and store as Parquet.

        Returns:
            None
        """        
        keys = []
        classifiers = []
        vectors_list = []
        file_key = f'{self.config.classification_prefix}/{self.classifier_id}/{self.classifier_id}.parquet'
        for key, vector_list in data['samples'].items():
            for vector in vector_list:
                keys.append(key)
                classifiers.append(data['classifier'])
                vectors_list.append(vector)

        values = [val for sublist in vectors_list for val in sublist]
        offsets = [0]
        current_offset = 0
        for vector in vectors_list:
            current_offset += len(vector)
            offsets.append(current_offset)
        keys_array = pa.array(keys, pa.string())
        classifiers_array = pa.array(classifiers, pa.string())
        values_array = pa.array(values, pa.float64())
        vectors_array = pa.ListArray.from_arrays(pa.array(offsets), values_array)
       
        samples = pa.Table.from_arrays([classifiers_array, keys_array, vectors_array], names=['classifier', 'class', 'vector'])
        try:
            if update:                
                obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
                body = obj['Body'].read()
                bytes_io = io.BytesIO(body)
                existing_samples = pq.read_table(bytes_io)

            local_file_path = os.path.join(self.cache_dir, f'{self.classifier_id}.parquet')
            if update:
                updated_samples = pa.concat_tables([existing_samples, samples])
                pq.write_table(updated_samples, local_file_path)
            else:
                pq.write_table(samples, local_file_path)
                
            self._upload_to_s3(local_file_path, file_key)            
        except Exception as e:
            logger.error(f"Error in reading existing samples from classifier: {str(e)}")
            raise e
        else:
            shutil.rmtree(self.cache_dir)
            
    def _gen_embedding(self, body: Any) -> List[Any]:
        """
        Bedrock Embdedding model API call

        Returns:
            List[Any]: An embedding vector.
        """
        model_invoke = Invocations(body=body,
                                   bedrock_client=self.bedrock_client,
                                   model_id=self.modelID)
        return model_invoke.invoke_embedding()

    def _gen_embeddings(self, base64_list: Dict[str, List[Any]], update: bool=False) -> None:
        """
        Bulk Bedrock Embdedding model API call for all classes and their samples

        Returns:
            None
        """
        max_workers = 10
        embed_errs = False
        os.makedirs(self.cache_dir, exist_ok=True)

        combined_embeddings = {k: [] for k in base64_list.keys()} 
        exceptions = {k: [] for k in base64_list.keys()}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self._gen_embedding, {
                "inputImage": f["base64string"],
                "embeddingConfig": {"outputEmbeddingLength": 256}
            }): (k, f["file_path"]) for k, files in base64_list.items() for f in files}

            for future in as_completed(futures):
                k, file_path = futures[future]
                try:
                    embedding = future.result()
                    combined_embeddings[k].append(embedding)
                except Exception as e:
                    embed_errs = True
                    error_message = f"Error processing {file_path}: {str(e)}"
                    logger.error(error_message)
                    exceptions[k].append({"file_path": file_path, "error": error_message})

        if embed_errs:
            self._save_to_s3(json_data=exceptions,
                             file_name=f"{self.classifier_id}_embeddings.error")
        
        classifier_samples = {
            "classifier": self.classifier_id,
            "samples": combined_embeddings
        }        
        
        self._embeddings_to_pq(data=classifier_samples, update=update)
        # with open(f'{self.cache_dir}/embeddings.json', 'w') as f:
        #     json.dump(classifier_samples, f)

    def _convert_to_base64(self, file_path: str, page: int) -> List[Dict[str, Any]]:
        """
        Converts page images to Base64 strings

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the base64 string of pages.
        """
        converter = FileConverter(file_path=file_path, 
                                  pages=[page], 
                                  s3_client=self.s3_client)
        return converter.convert_to_base64()

    def _batch_convert_to_base64(self, manifest_content: Dict[str, List[Tuple[str, int]]]) -> Dict[str, List[Any]]:
        """
        Bulk Converts page images to Base64 strings using ThreadPoolExecutor

        Returns:
            Dict[str, List[Any]]: A dictionary of all the classes and their corresponding sample document's
            base64 image strings for vector sampling.
        """
        max_workers = 4 
        conversion_err = False
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for k, file_info in manifest_content.items():
                for file_path, page in file_info:
                    future = executor.submit(self._convert_to_base64, file_path, page)
                    futures[future] = (k, file_path)

            base64_results = {k: [] for k in manifest_content}
            exceptions = {k: [] for k in manifest_content}

            for future in as_completed(futures):
                k, file_path = futures[future]
                try:
                    response = future.result()
                    for result in response:
                        base64_results[k].append({
                            "file_path": file_path,
                            "base64string": result['base64string']
                        })
                except Exception as e:
                    conversion_err = True
                    error_message = f"Error processing {file_path}: {str(e)}"
                    logger.error(error_message)
                    exceptions[k].append({"file_path": file_path, "error": error_message})
        if conversion_err:
            self._save_to_s3(json_data=exceptions,
                            file_name=f"{self.classifier_id}_conversion.error")
        return base64_results
    
    def run_sampler(self, manifest_data: Any, update_classifier: Optional[str] = None) -> str:
        """
        Runs the core classification vector sampling process using the manifest 
        file provided

        Returns:
            str: The unique classifier ID
        """
        
        update = False
        if update_classifier:
            self.classifier_id = update_classifier
            # check if the classifer exists            
            update = self._check_valid_classifier(object_path=f"{self.config.classification_prefix}/{self.classifier_id}/{self.classifier_id}.parquet")

        sample_source = manifest_data # self._process_manifest()
        base64_list = self._batch_convert_to_base64(manifest_content=sample_source)
        self._gen_embeddings(base64_list=base64_list, update=update)
        return self.classifier_id
    
    def view_classifier(self, classifier_id: str) -> List[Dict[str, Any]]:
        """
        View details of a particular classifier, i.e. the Class labels and the
        number of vector samples per class.

        Args:
            - `classifier_id` (`str`): The classifier ID

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing class labels and sample counts 
        """
        
        file_key=f"{self.config.classification_prefix}/{classifier_id}/{classifier_id}.parquet"
        try:
            self._check_valid_classifier(object_path=file_key)
            obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            body = obj['Body'].read()
            bytes_io = io.BytesIO(body)
            table = pq.read_table(bytes_io)

            value_counts_result = pc.value_counts(table["class"])
            unique_values = value_counts_result.field("values")
            counts = value_counts_result.field("counts")
            unique_values_list = unique_values.to_pylist()
            counts_list = counts.to_pylist()

            data = []
            for value, count in zip(unique_values_list, counts_list):
                data.append({
                    "class": value,
                    "num_samples": count
                })
            return data
        except Exception as e:
            raise e