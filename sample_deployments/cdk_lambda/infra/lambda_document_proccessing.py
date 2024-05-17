from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_lambda,
    aws_iam,
    aws_s3
)
from constructs import Construct
from pathlib      import Path

class SampleDeploymentsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = aws_s3.Bucket(self, "MyLambdaBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )


        lambda_function =  self.__create_lambda_function("document-processing-lambda", bucket)
        srole_bedrock = aws_iam.Role(
            scope      = self,
            id         = f'srole-bedrock',
            assumed_by = aws_iam.ServicePrincipal('bedrock.amazonaws.com') 
        )

        srole_bedrock.grant_pass_role(lambda_function)
        
        lambda_function.role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonBedrockFullAccess')
        )

        bucket.grant_read_write(lambda_function.role)

    def __create_lambda_function(self, function_name: str, bucket: aws_s3.Bucket):

        lambda_role = aws_iam.Role(self, 'LambdaExecutionRole',
            assumed_by=aws_iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')]
        )
        
        lambda_function = aws_lambda.DockerImageFunction(
                scope=self,
                id=function_name,
                function_name=function_name,
                code=aws_lambda.DockerImageCode.from_image_asset(directory=f"{Path('source/lambda').absolute()}"),
                timeout=Duration.minutes(15),
                memory_size=3000,
                role=lambda_role,
                environment={
                    'BUCKET_NAME': bucket.bucket_name 
                }
        )

        return lambda_function
