#!/bin/bash

# Uninstall rhubarb_dev
pip uninstall pyrhubarb -y

# Build the package
poetry build

# Install the package
# poetry install

# install the built package
pip install dist/pyrhubarb-0.0.1-py3-none-any.whl