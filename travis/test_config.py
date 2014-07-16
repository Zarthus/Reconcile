"""
Travis Test file:
Test the config.json for JSON errors.
"""

import json
import sys


try:
    json.load(open("config.json"))
except Exception as e:
    print("Travis: 'json.load' threw exception:\n{}".format(str(e)))
    sys.exit(1)

print("Travis: config.json is a valid JSON document!")
