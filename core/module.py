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

Module handler -- handles the loading, unloading, and sending instructions to modules.
"""

import os
import importlib
import inspect
import traceback


class ModuleHandler:

    def __init__(self, conn):
        self._conn = conn
        self.logger = self._conn.logger

        self.modules = {}
        self.module_dir = "modules"

    def sendConnect(self):
        for module in self.modules:
            self.modules[module].on_connect()

    def sendDisconnect(self):
        for module in self.modules:
            self.modules[module].on_disconnect()

    def sendCommand(self, target, nick, command, commandtext, mod=False, admin=False):
        for module in self.modules:
            if self.modules[module].on_command(target, nick, command, commandtext, mod, admin):
                return True
        return False

    def sendPrivmsg(self, target, nick, message):
        for module in self.modules:
            self.modules[module].on_privmsg(target, nick, message)

    def sendAction(self, target, nick, message):
        for module in self.modules:
            self.modules[module].on_action(target, nick, message)

    def sendJoin(self, nick, channel):
        for module in self.modules:
            self.modules[module].on_join(nick, channel)

    def sendSelfJoin(self, channel):
        for module in self.modules:
            self.modules[module].on_self_join(channel)

    def sendSelfPart(self, channel):
        for module in self.modules:
            self.modules[module].on_self_part(channel)

    def sendPart(self, nick, channel, message):
        for module in self.modules:
            self.modules[module].on_part(nick, channel, message)

    def sendKick(self, nick, channel, knick, reason):
        for module in self.modules:
            self.modules[module].on_kick(nick, channel, knick, reason)

    def sendQuit(self, nick, message):
        for module in self.modules:
            self.modules[module].on_quit(nick, message)

    def sendNumeric(self, numeric, data):
        for module in self.modules:
            self.modules[module].on_numeric(numeric, data)

    def loadAll(self):
        for module in self.getAvailableModulesList():
            if module in self.modules:
                self.logger.notice("Attempted to load module '{}', but it was already loaded.".format(module))
                continue

            self.load(module)

    def unloadAll(self):
        for module in self.modules:
            self.unload(module, False)
        self.modules = {}

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
                self.modules[module] = moduleclass(self._conn, self.logger, modulename)
                self.modules[module].on_module_load()
        except Exception as e:
            self.logger.error("Failed to load module {}: {}".format(module, str(e)))

            if "requires API key" not in str(e):  # The error is not related to API keys not existing, print the tb.
                traceback.print_exc()

            success = False
            self.unload(module)

        if success:
            self.logger.log("Successfully loaded module {}".format(module))

        return success

    def unload(self, module, pop=True):
        if module not in self.modules:
            return False

        self.modules[module].on_module_unload()
        self.modules[module]._unregister_commands()
        if pop:
            del self.modules[module]
        self.logger.log("Unloaded module {}".format(module))

        return True

    def reload(self, module):
        unloaded_fine = self.unload(module)
        loaded_fine = self.load(module)
        return unloaded_fine and loaded_fine

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
