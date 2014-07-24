"""
Module handler -- handles the loading, unloading, and sending instructions to modules.
"""

import os
import importlib
import inspect
import modules


class ModuleHandler:

    def __init__(self, conn):
        self._conn = conn
        self.logger = self._conn.logger

        self.modules = {}
        self.module_dir = "modules"

    def sendCommand(self, target, nick, command, commandtext, mod=False, admin=False):
        for module in self.modules:
            if self.modules[module].on_command(target, nick, command, commandtext, mod, admin):
                break

    def sendPrivmsg(self, target, nick, message):
        for module in self.modules:
            self.modules[module].on_privmsg(target, nick, message)

    def sendAction(self, target, nick, message):
        for module in self.modules:
            self.modules[module].on_action(target, nick, message)

    def loadAll(self):
        for module in self.getAvailableModulesList():
            if module in self.modules:
                self.logger.notice("Attempted to load module '{}', but it was already loaded.".format(module))
                continue

            self.load(module)

    def unloadAll(self):
        for module in self.modules:
            self.unload(module)

    def reloadAll(self):
        for module in self.modules:
            self.reload(module)

    def load(self, module):
        if module in self.modules:
            self.logger.notice("Attempted to load module '{}', but it was already loaded.".format(module))
            return False

        success = True

        try:
            mod = importlib.import_module("{}.{}".format(self.module_dir, module[:-3]))

            for modulename, moduleclass in inspect.getmembers(mod, inspect.isclass):
                self.modules[module] = moduleclass(self._conn, self.logger, module)
                self.modules[module].on_module_load()
        except Exception as e:
            self.logger.error("Failed to load module {}: {}".format(module, str(e)))
            success = False
            self.unload(module)

        if success:
            self.logger.log("Successfully loaded module {}".format(module))
        else:
            self.logger.notice("Failed to load module {}".format(module))

        return success

    def unload(self, module):
        if module not in self.modules:
            return False

        self.modules[module].on_module_unload()
        self.modules[module]._unregister_commands()
        self.modules = self.modules.pop(module)
        self.logger.log("Unloaded module {}".format(module))

        return True

    def reload(self, module):
        self.unload(module)
        self.load(module)

    def getLoadedModulesList(self):
        loaded_modules = []

        for module in self.modules:
            loaded_modules.append(module)

        return loaded_modules

    def getAvailableModulesList(self):
        available_modules = []

        for file in os.listdir(self.module_dir):
            if file == "__init__.py" or file.endswith(".pyc") or os.path.isdir(os.path.join(self.module_dir, file)):
                continue

            available_modules.append(file)

        return available_modules
