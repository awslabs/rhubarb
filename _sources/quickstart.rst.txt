Quickstart
==========

This guide details the steps needed to install or update Rhubarb.


Installation
------------

You will need Python 3.9 or above to use Rhubarb.

Install or update Python
~~~~~~~~~~~~~~~~~~~~~~~~

Before installing Boto3, install Python 3.9 or later. For information about how to get the latest version of Python, see the official `Python documentation <https://www.python.org/downloads/>`_. 

Install Rhubarb
~~~~~~~~~~~~~~~

Rhubarb official package is available on PyPI and can be installed with

.. code-block:: bash

    pip install pyrhubarb

By default this will install the latest version of Rhubarb.


From Source
~~~~~~~~~~~

To install the package, clone the repository with the following command -

.. code-block:: bash

    git clone git@github.com:awslabs/rhubarb.git

Navigate into the project directory on the terminal and perform the following steps.

1. It is recommended you use python virtual environment such as :code:`venv` using :code:`python -m venv rhubarb`.
2. Activate :code:`venv` using :code:`source rhubarb/bin/activate`.
3. Rhubarb is built and packaged using `Poetry <https://python-poetry.org/docs/>`_. You will need to `install Poetry <https://python-poetry.org/docs/#installation>`_.
4. Perform :code:`poetry install` from the root of the project i.e. where the :code:`pyproject.toml` file resides. This will install all the dependencies including Rhubarb.
5. Install :code:`pre-commit` hooks using :code:`pre-commit install`. This will setup :code:`ruff` linter and formater checks before your changes are committed to the repo.
6. Install dependencies using :code:`poetry install`.
7. Build the project using :code:`poetry build`.
8. Poetry will create a :code:`whl` file within a :code:`dist/` directory which can be installed.


.. code-block:: bash

    pip install pyrhubarb-0.0.1-py3-none-any.whl


Configuration
-------------

.. note:: You must have Anthropic Claude V3 model and Amazon Titan Multi-modal Embedding model access enabled in Amazon Bedrock. To enable models, see `Amazon Bedrock documentation <https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html>`_.

Before using Boto3, you need to set up authentication credentials for your AWS account using either
the `IAM Console <https://console.aws.amazon.com/iam/home>`_ or the AWS CLI. You can either choose
an existing user or create a new one.

For instructions about how to create a user using the IAM Console, see `Creating IAM users
<https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console>`_.
Once the user has been created, see `Managing access keys
<https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey>`_
to learn how to create and retrieve the keys used to authenticate the user.

If you have the `AWS CLI <http://aws.amazon.com/cli/>`_ installed, then you can use the
:command:`aws configure` command to configure your credentials file::

    aws configure

Alternatively, you can create the credentials file yourself. By default, its location is
``~/.aws/credentials``. At a minimum, the credentials file should specify the access key and secret
access key. In this example, the key and secret key for the account are specified in the ``default`` profile::

    [default]
    aws_access_key_id = YOUR_ACCESS_KEY
    aws_secret_access_key = YOUR_SECRET_KEY

You may also want to add a default region to the AWS configuration file, which is located by default
at ``~/.aws/config``::

    [default]
    region=us-east-1

Alternatively, you can pass a ``region_name`` when creating clients and resources.

You have now configured credentials for the default profile as well as a default region to use when
creating connections. See `Boto3 configuration <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#guide-configuration>`_ for in-depth configuration sources and options.

Using Rhubarb
-------------

Using with a local file

.. code:: python

    from rhubarb import DocAnalysis
    import boto3

    session = boto3.Session()
    da = DocAnalysis(file_path="./path/to/doc/doc.pdf", boto3_session=session)
    response = da.run(message="What is the employee's name?")   

With file in Amazon S3

.. code:: python

    from rhubarb import DocAnalysis
    import boto3

    session = boto3.Session()
    da = DocAnalysis(file_path="s3://path/to/doc/doc.pdf", boto3_session=session)
    response = da.run(message="What is the employee's name?")