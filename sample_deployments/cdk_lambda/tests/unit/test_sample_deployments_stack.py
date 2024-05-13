import aws_cdk as core
import aws_cdk.assertions as assertions

from sample_deployments.sample_deployments_stack import SampleDeploymentsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in sample_deployments/sample_deployments_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SampleDeploymentsStack(app, "sample-deployments")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
