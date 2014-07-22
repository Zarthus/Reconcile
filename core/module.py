"""
Module handler -- handles the loading, unloading, and sending instructions to modules.
"""

import os


class ModuleHandler:

    def __init__(self):
        self.modules = {}
        self.module_dir = "modules/"

    def sendCommand(self, target, nick, command, commandtext, mod=False, admin=False)
        for module in self.modules:
            if module.on_command(target, nick, command, commandtext, mod, admin):
                break

    def sendPrivmsg(self, target, nick, message)
        for module in self.modules:
            module.on_privmsg(target, nick, message)

    def sendAction(self, target, nick, message)
        for module in self.modules:
            module.on_action(target, nick, message)

    def loadAll(self):
        for module in self.getAvailableModulesList():
            if module in self.modules:
                # TODO: Log
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
            # TODO: Log
            return False

        success = True

        try:
            mod = compile(open(self.module_dir + module).read(), module, 'exec')
            mod = mod.

            self.modules[module] =
            self.modules[module].on_module_load()
        except Exception as e:
            # TODO: Log
            success = False

        return success


    def unload(self, module):
        if module not in self.modules:
            return False

        self.modules[module].on_module_unload()
        self.modules = self.modules.pop(module)

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
            available_modules.append(file)

        return available_modules