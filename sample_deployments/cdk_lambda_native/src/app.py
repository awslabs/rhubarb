import json

import boto3

from rhubarb import DocAnalysis

session = boto3.Session()


def lambda_handler(event, context):
    da = DocAnalysis(
        file_path="s3://anjan-sonnet-rhubarb/scientific_paper.pdf", boto3_session=session
    )
    resp = da.run(message="What is ECVR?")

    return {"statusCode": 200, "body": json.dumps(resp)}
