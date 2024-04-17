## Developing and contrubuting to Rhubarb

1. Install `poetry` [https://python-poetry.org/docs/]. It is recommended you use python virtual environment such as `venv`.
2. Clone this repo and perform `poetry install` from the root of the project i.e. where the `pyproject.toml` file resides. This will install all the dependencies including Rhubarb.
3. Install `pre-commit` hooks using `pre-commit install`. This will setup `ruff` linter and formater checks before your changes are committed to the repo. _(See below in case you see "Cowardly refusing to install" error)_
4. Make changes to the core Rhubarb code, in case you are adding features, fixing bugs etc.
5. Once you make changes perfrom `poetry build` and subsequently `poetry install`. Or run the build script `./build_install.sh`.

## Error installing `pre-commit` hook

You may encounter `Cowardly refusing to install` error with `pre-commit` if you have `git defender` installed. In that case run the following commands

```bash
git config --system --unset-all core.hookspath # if this shows permission denied, use sudo
pre-commit install
git defender --install
```

## Before committing

> :warning: You DO NOT have to perform this manually since the `pre-commit` hook is set to run this prior to comitting into the repo. However, if you would like to run the linter and formatter before you get to the stage of committing your changes, then you can run the commands mentioned below manually.

We are striving to follow best practices with our codebase, as such this project uses `ruff` for linter and re-formatter. `ruff` can scan your code and find issues that you can easily address, and can help fix most of the common issues with code.

- Run `poetry run ruff check` to ensure best practices. If everything is good you should see `All checks passed!`, else go to next step.
- You can run `poetry run ruff check --fix` which will perform some of the code formatting issues found. It's not perfect but it will get you there almost to a very good code rating. Some of the common things it does 
  - Checks and fixes long lines of code
  - Checks and fixes unused variables
  - Checks and flags unused imports
  - Sorts and groups imports etc.

## `git commit` fails to commit

You may receive error when comitting your changes.

```
ruff.....................................................................Passed
ruff-format..............................................................Failed
- hook id: ruff-format
- files were modified by this hook

X files reformatted
command error
```

This simply means that the pre-commit hook with `ruff` did it's job and re-formatted some of the new files/lines of code you added. If this happens, simply perform `git add` and `git commit` again the commit the changes.

## Testing with Python Notebooks

You can test your changes using the Python notebooks found in [cookbooks](./cookbooks/) directory. To efficiently do that, we recommend using Python virtual environment such as `venv`. If you're using `venv` here are are the general steps.

```bash
python -m venv rhubarb      # rhubarb is the name of your venv
source rhubarb/bin/activate # activate the venv
./build_install             # Build the project and install the library in your venv
```

If you wish to use the cookbok Python notebooks then install `jupyter` and `ipykernel` in the virtual environment as well.

```bash
pip install ipykernel jupyter
```

Once you follow the above steps, you should be able to select `rhubarb` virtual environment as the Kernel for your notebook. You will also need to have AWS credentials setup with `aws configure` in your dev environment for the notebooks to work. See this [documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) for setting up AWS CLI. Ideally, you should have a [named profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html#cli-configure-files-using-profiles) setup with AWS configure, for your AWS credentials. If you have all of it setup correctly then in the notebook you can pass `profile_name=<your-profile-name>` everywhere `boto3.Session` is used, for example-

```python
import boto3
session = boto3.Session(profile_name="<your-profile-name>")
```

## Scan Dependencies Locally

If you add new project dependencies you might want to scan the dependencies for vulnerabilities. Install `pip-audit` in the python `venv`. 

```bash
pip install pip-audit
```

Once done, run the following command to generate `requirements.txt`. Since the project uses Poetry, you will need to instead generate `requirements.txt` and scan that with `pip-audit`.

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

Once the `requirements.txt` is generated (or updated), run the `pip-audit` command below-

```bash
pip-audit -r requirements.txt
```