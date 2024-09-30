# Deploy an AWS Lambda with a Lambda Layer with Rhubarb

This is a temlate CDK project demonstrating deployment of a Lambda function with Rhubarb as a Lambda layer without using docker images. To execute this CDK project, follow the steps below -

1. While in the `cdk_lambda_native` directory, run `npm install --save` to install the dependencies.
2. Update the `bin/cdk_lambda_native.js` file with your AWS account ID and region and.
3. Run `cdk bootstrap`. ([Learn more about CDK Bootstrapping](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html))
4. Optional: Edit the Lambda function code in `src/app.py` to add your custom logic.
5. Optional: To edit the stack make changes to the `lib/cdk_lambda_native-stack.js` file.
6. Run `cdk deploy` to deploy the stack.
7. Optional: to delete the stack, run `cdk destroy`

The `cdk.json` file tells the CDK Toolkit how to execute your app. The build step is not required when using JavaScript.

NOTE: This is deployment will not work for v0.0.1 and v0.0.2

## Useful commands

* `npm run test`         perform the jest unit tests
* `npx cdk deploy`       deploy this stack to your default AWS account/region
* `npx cdk diff`         compare deployed stack with current state
* `npx cdk synth`        emits the synthesized CloudFormation template
