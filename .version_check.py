#!/usr/bin/env python
#
# The MIT License (MIT)
#
# Copyright (c) 2014 - 2015 Jos "Zarthus" Ahrens and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# .version_check.py:  Read the version from the example configuration, and update the regular, .gitignored, config.
# This script is overly verbose.  To prevent it from printing data, set `verbose` to False.
#
# Command line arguments:
#  be_verbose: numerical value (0 or 1) that tells us to be verbose or not.
#
# Exit codes:
#  0  - all is good.
#  1  - cannot find example config file
#  2  - cannot find actual config file
#  3  - failed to load example config as json
#  4  - failed to load actual config as json
#  5  - failed to find bot_version in example config
#  6  - failed to find bot_version in actual config
#  7  - could not replace versions.
#  8  - an error occured while writing version to config.

import json
import os
import re
import sys


exampleconf = "config.example.json"  # path to example config file.
actualconf = "config.json"  # path to used config file
verbose = None

if len(sys.argv) >= 2:
    if sys.argv[1].isnumeric():
        try:
            verbose = bool(int(sys.argv[1]))
        except ValueError:
            pass

if not verbose:
    verbose = False

# Match 1.2, 1.2.3, 1.2.3-dev, capturing 1 as major version, 2 as minor version, 3 as build number, and dev as extra
version_regex = re.compile(r"(\d+)\.(\d+)(?:\.(\d+))?(?:\-([a-zA-Z0-9]+))?")


def log(s, verbose=True):
    if verbose:
        print(s)

if not os.path.isfile(exampleconf):
    log("Could not find example config (path: '{}') to read newest version from.".format(exampleconf), verbose)
    sys.exit(1)

if not os.path.isfile(actualconf):
    log("Could not find actual config (path: '{}') to read older or current version from.".format(actualconf), verbose)
    sys.exit(2)

try:
    example_json = json.load(open(exampleconf))
except Exception as e:
    log("Failed to load example config as json: {}".format(str(e)), verbose)
    sys.exit(3)

try:
    actual_json = json.load(open(actualconf))
except Exception as e:
    log("Failed to load actual config as json: {}".format(str(e)), verbose)
    sys.exit(4)

if "metadata" not in example_json or "bot_version" not in example_json["metadata"]:
    log("Could not find bot_version in example config.", verbose)
    sys.exit(5)

if "metadata" not in actual_json or "bot_version" not in actual_json["metadata"]:
    log("Could not find bot_version in example config.", verbose)
    sys.exit(6)

example_version = example_json["metadata"]["bot_version"]
actual_version = actual_json["metadata"]["bot_version"]

log("Version Compare: (new) {} == {} (old)".format(example_version, actual_version), verbose)

if example_version == actual_version:
    log("Versions are up to date.  No need to edit existing configuration.", verbose)
    sys.exit(0)
else:
    log("Version outdated.  Will attempt to update now.", verbose)

example_match = version_regex.match(example_version)
actual_match = version_regex.match(actual_version)

if not example_match or not example_match.groups():
    log("Example version did not match expected value.", verbose)
    sys.exit(7)

if not actual_match or not actual_match.groups():
    log("Actual version did not match expected value.", verbose)
    log("Setting actual version to '{}'".format(example_version), verbose)

actual_json["metadata"]["bot_version"] = example_version

try:
    json.dump(actual_json, open(actualconf, "w"))
except IOError as e:
    log("Failed to write new version: {}".format(str(e)), verbose)
    sys.exit(8)
except Exception as e:
    log("Unexpected error when attempting to write new version: {}".format(str(e)), verbose)
    sys.exit(8)

log("Actual version set to '{}' (old version: '{}')".format(example_version, actual_version), verbose)

