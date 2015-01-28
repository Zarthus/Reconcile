"""
The MIT License (MIT)

Copyright (c) 2014 - 2015 Jos "Zarthus" Ahrens and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Validate a module
"""

import sys
import os
import re


check_modules = []
failcount = 0
checklist = []
errorlist = []

if len(sys.argv) == 1:
    print("No module specified, checking them all.")

    # Check against disabled modules, those that are not empty are appended to a list.
    dmods = os.listdir("modules_disabled")
    dismods = []
    for dismod in dmods:
        if os.stat(os.path.join("modules_disabled", dismod)).st_size:
            dismods.append(dismod)

    for file in sorted(os.listdir("modules") + dismods):
        if (file == "__init__.py" or file.endswith(".pyc") or os.path.isdir(os.path.join("modules", file))):
            continue
        check_modules.append(file)
else:
    for mod in sorted(sys.argv[1:]):
        check_modules.append(mod)


def check_module(module_name):
    if (not os.path.exists(os.path.join("modules", module_name)) and
            not os.path.exists(os.path.join("modules_disabled", module_name))):
        print("Module {} does not exist.".format(module_name))
        return 1

    requirements = {
        "imports_template": False,
        "extends_template": False,
        "utilises_callback": False,
        "utilises_logger": True,  # Check against use of print() instead of self.logger.log
        "does_not_call_logger_directly": True  # Check if self.log over self.logger.log was used.
    }

    optional = {
        "requires_api_key": False,
        "registers_commands": False,
        "has_configuration_block": False,
        "uses_rate_limitation": False
    }

    confblock_func = []
    ratelimited_commands = []

    error_count = 0

    f = None
    if os.path.exists(os.path.join("modules", module_name)):
        f = open(os.path.join("modules", module_name)).read().split("\n")
    elif os.path.exists(os.path.join("modules_disabled", module_name)):
        f = open(os.path.join("modules_disabled", module_name)).read().split("\n")
    else:
        print("Module {} does not exist".format(module_name))
        return 1

    print("\nChecking module {} for any errors".format(module_name))

    ratelimit_regex = re.compile(r"self\.ratelimit\((.*)\)")

    line_num = 0
    for line in f:
        line_num += 1
        line = line.lower().strip()

        if line.startswith("from core import moduletemplate"):
            requirements["imports_template"] = True

        if line.endswith("(moduletemplate.botmodule):"):
            requirements["extends_template"] = True

        if line.startswith("def on_"):
            requirements["utilises_callback"] = True

        if line.startswith("print("):
            requirements["utilises_logger"] = False

        if line.startswith("self.logger."):
            requirements["does_not_call_logger_directly"] = False

        if line.startswith("self.requireapikey"):
            optional["requires_api_key"] = True

        if line.startswith("self.register_command("):
            optional["registers_commands"] = True

        if ratelimit_regex.search(line):
            optional["uses_rate_limitation"] = True
            optional["has_configuration_block"] = True

            cmdname = ""

            params = ratelimit_regex.search(line).group(1)

            if "," in params:
                params = params.split(",")

                if len(params) > 1:
                    cmdname = params[0]
                    confblock_func.append(params[1])
                else:
                    cmdname = params[0]
                    confblock_func.append("rate_limit_delay")
            else:
                cmdname = params
                confblock_func.append("rate_limit_delay")

            if ((cmdname.startswith("\"") or cmdname.startswith("'")) and
               (cmdname.endswith("\"") or cmdname.endswith("'"))):
                ratelimited_commands.append(cmdname.replace("\"", "").replace("'", ""))
            else:
                ratelimited_commands.append("line:{} var:{}".format(line_num, cmdname))

        if "self.module_data" in line:
            optional["has_configuration_block"] = True
            for word in line.split():
                if word.startswith("self.module_data["):
                    funcname = ''

                    try:
                        funcname = word.split("\"")[1]
                    except Exception:
                        funcname = word.split("'")[1]

                    confblock_func.append(funcname)

    ratelimited_commands = list(set(ratelimited_commands))
    confblock_func = list(set(confblock_func))

    for requirement in requirements.items():
        if requirement[1]:
            print("  [x] Requirement satisfied: {}".format(requirement[0].replace("_", " ")))
        else:
            print("  [ ] Requirement NOT met: {}".format(requirement[0].replace("_", " ")))
            error_count += 1

    for opt in optional.items():
        if opt[1]:
            print("  [x] Optional checks: This module: {}".format(opt[0].replace("_", " ")))

    for func in confblock_func:
        print("  Introduces module block configuration: {}".format(func))

    for cmd in ratelimited_commands:
        print("  Ratelimitation on: {}".format(cmd))

    print("check_module('{}') ran with {} errors.\n"
          .format(module_name, error_count))

    return error_count

for module in check_modules:
    if not module.endswith(".py"):
        module + ".py"

    check = check_module(module)

    if check > 0:
        failcount += check
        errorlist.append(module)

    checklist.append(module)

print("A total of {}/{} modules errored with a total of {} errors.".format(len(errorlist), len(checklist), failcount))
print("The following modules were checked: " + str(checklist))
print("The following modules were errored: " + str(errorlist) + "\n")

sys.exit(failcount)
