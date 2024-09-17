FROM public.ecr.aws/lambda/python:3.12-x86_64

# Upgrade pip
RUN /var/lang/bin/python -m pip install --upgrade pip

# Copy the requirements file
COPY /requirements.txt /tmp/

# Copy the requirements file
RUN python -m pip install -r /tmp/requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy lambda code
COPY /handler.py  ${LAMBDA_TASK_ROOT}


WORKDIR ${LAMBDA_TASK_ROOT}

# Set the command to launch the Lambda handler
CMD ["handler.lambda_handler"]