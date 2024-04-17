#!/bin/bash

# Uninstall rhubarb_dev
pip uninstall rhubarb -y

# Build the package
poetry build

# Install the package
# poetry install

# install the built package
pip install dist/rhubarb-0.0.1a1-py3-none-any.whl