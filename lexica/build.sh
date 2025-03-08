#!/bin/sh

# This script runs all of the lexica generation scripts

set -x
uv run --script anatomy/generate.py
uv run --script cell/generate.py
uv run --script phenotype/generate.py
uv run --script obo/generate.py
