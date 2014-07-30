#!/bin/bash
# This script has only been tested (and most likely only works) on linux machines.
# This script can be used to see if the commit(s) you are about to make will work with travis.

flake8 .
echo
python3 travis/test_module.py | tail -4

