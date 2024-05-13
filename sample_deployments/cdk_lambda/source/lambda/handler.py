from      os import getenv
from rhubarb import DocAnalysis
import boto3

class ProcessDocument():
    def generateJSON(self, document):
        try:
            session = boto3.Session()

            da = DocAnalysis(file_path=document,
                        boto3_session=session,
                        pages=[1])
            prompt="I want to extract the employee name, employee SSN, employee address, \
                    date of birth and phone number from this document."
            resp = da.generate_schema(message=prompt)
            response = da.run(message=prompt,
                            output_schema=resp['output']
            )
        except (
            # handle bedrock or S3 error
        ) as e:

            return None

        return response



def lambda_handler(event, context):
    BUCKET_NAME = getenv('BUCKET_NAME')

    documentURL = f's3://{BUCKET_NAME}/employee_enrollment.pdf'
    
    result = ProcessDocument().generateJSON(documentURL)

    return result