"""Validate a module"""

import sys
import os


check_modules = []
failcount = 0
checklist = []
errorlist = []

if len(sys.argv) == 1:
    print("No module specified, checking them all.")

    for file in os.listdir("modules"):
        if file == "__init__.py" or file.endswith(".pyc") or os.path.isdir(os.path.join("modules", file)):
            continue
        check_modules.append(file)
else:
    for mod in sys.argv[1:]:
        check_modules.append(mod)


def check_module(module_name):
    if not os.path.exists(os.path.join("modules", module_name)):
        print("{} -- file does not exist.".format(module_name))
        return 1

    requirements = {
        "imports_template": False,
        "extends_template": False,
        "utilises_callback": False,
        "utilises_logger": False,  # Check against use of print() instead of self.logger.log
    }

    optional = {
        "requires_api_key": False,
        "registers_commands": False,
    }

    error_count = 0

    f = open(os.path.join("modules", module_name)).read().split("\n")

    print("\nChecking module {} for any errors".format(module_name))

    for line in f:
        line = line.lower().strip()

        if line.startswith("from core import moduletemplate"):
            requirements["imports_template"] = True

        if line.endswith("(moduletemplate.botmodule):"):
            requirements["extends_template"] = True

        if line.startswith("def on_"):
            requirements["utilises_callback"] = True

        if line.startswith("print("):
            requirements["utilises_logger"] = True

        if line.startswith("requireapikey"):
            optional["requires_api_key"] = True

        if line.startswith("self.register_command("):
            optional["registers_commands"] = True

    for requirement in requirements.items():
        if requirement[1]:
            print("  [x] Requirement satisfied: {}".format(requirement[0].replace("_", " ")))
        else:
            print("  [ ] Requirement NOT met: {}".format(requirement[0].replace("_", " ")))
            error_count += 1

    for opt in optional.items():
        if opt[1]:
            print("  [x] Optional checks: This module: {}".format(opt[0].replace("_", " ")))

    print("check_module('{}') ran with {} errors, information was printed to the console.\n"
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
