#!/bin/bash
rm -rf .venv
virtualenv .venv && source .venv/bin/activate
pip install .
