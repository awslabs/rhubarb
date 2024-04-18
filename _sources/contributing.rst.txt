Contributing
============

This guide walks you through the steps that needs to be taken in order to setup the project workspace for Rhubarb. Once you have 
completed the steps in this guide you should be able to make code changes and test Rhubarb locally.

1. It is recommended you use python virtual environment such as :code:`venv` using :code:`python -m venv rhubarb`.
2. Activate :code:`venv` using :code:`source rhubarb/bin/activate`.
3. Rhubarb is built and packaged using `Poetry <https://python-poetry.org/docs/>`_. You will need to `install Poetry <https://python-poetry.org/docs/#installation>`_.
4. Perform :code:`poetry install` from the root of the project i.e. where the :code:`pyproject.toml` file resides. This will install all the dependencies including Rhubarb.
5. Install :code:`pre-commit` hooks using :code:`pre-commit install`. This will setup :code:`ruff` linter and formater checks before your changes are committed to the repo.
6. Install dependencies using :code:`poetry install`.
7. Build the project using :code:`poetry build`.
8. Poetry will create a :code:`whl` file within a :code:`dist/` directory which can be installed.

Error installing :code:`pre-commit` hook
----------------------------------------

You may encounter `Cowardly refusing to install` error with :code:`pre-commit` if you have :code:`git defender` installed. In that case run the following commands

.. code:: bash

    git config --system --unset-all core.hookspath # if this shows permission denied, use sudo
    pre-commit install
    git defender --install

Before committing
-----------------

.. note:: You DO NOT have to perform this manually since the :code:`pre-commit` hook is set to run this prior to comitting into the repo. However, if you would like to run the linter and formatter before you get to the stage of committing your changes, then you can run the commands mentioned below manually.

We are striving to follow best practices with our codebase, as such this project uses :code:`ruff` for linter and re-formatter. :code:`ruff` can scan your code and find issues that you can easily address, and can help fix most of the common issues with code.

- Run :code:`poetry run ruff check` to ensure best practices. If everything is good you should see :code:`All checks passed!`, else go to next step.
- You can run :code:`poetry run ruff check --fix` which will perform some of the code formatting issues found. It's not perfect but it will get you there almost to a very good code rating. Some of the common things it does 
  - Checks and fixes long lines of code
  - Checks and fixes unused variables
  - Checks and flags unused imports
  - Sorts and groups imports etc.

:code:`git commit` fails to commit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may receive error when comitting your changes.

.. code:: 

     ruff.....................................................................Passed
     ruff-format..............................................................Failed
     - hook id: ruff-format
     - files were modified by this hook

     X files reformatted
     command error


This simply means that the pre-commit hook with :code:`ruff` did it's job and re-formatted some of the new files/lines of code you added. If this happens, 
simply perform :code:`git add` and then :code:`git commit -m <message>` again to commit the changes.