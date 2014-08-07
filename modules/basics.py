"""
Basic commands by Zarthus
Licensed under MIT

This is a series of basic commands any bot really should have.
"""

from core import moduletemplate


class BasicCommands(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("permissions", None, "Show if you are a bot administrator or moderator", self.PRIV_NONE)
        self.register_command("ping", None, "Make the bot reply with a message to see if it is still there.",
                              self.PRIV_NONE)
        self.register_command("commands", "[module]", "List all commands or from those from [module]",
                              self.PRIV_NONE)
        self.register_command("commandinfo", "<command>", "Display information about <command>", self.PRIV_NONE)
        self.register_command("help", "[command]", "Display help information about [command] or list all commands",
                              self.PRIV_NONE)
        self.register_command("join", "<channel[,channel]>", "Join a comma separated list of channels.",
                              self.PRIV_MOD)
        self.register_command("part", "<channel[,channel]>", "Leave a comma separated list of channels.",
                              self.PRIV_MOD)
        self.register_command("nick", "<new nick>", "Change name to <new nick> if available.",
                              self.PRIV_MOD)
        self.register_command("message", "<target> <message>", "Message <target> with <message>.", self.PRIV_MOD)
        self.register_command("loadedmodules", None, "Display a list of loaded modules.", self.PRIV_MOD,
                              ["mod", "modules"])
        self.register_command("availablemodules", None, "Display a list of available modules.", self.PRIV_MOD,
                              ["amod"])
        self.register_command("shutdown", None,
                              "Shut the entire bot down. This includes connections to different networks",
                              self.PRIV_ADMIN)
        self.register_command("rehash", "[reconnect]",
                              "Rehash the bots configuration, use 'rehash reconnect' if you want the bot to reconnect",
                              self.PRIV_ADMIN)
        self.register_command("reconnect", None, "Tell the bot to reconnect to the network.", self.PRIV_ADMIN)
        self.register_command("loadmodule", "<module>", "Loads a <module>", self.PRIV_ADMIN, ["lmod"])
        self.register_command("unloadmodule", "<module>", "Unloads a <module>", self.PRIV_ADMIN, ["umod"])
        self.register_command("reloadmodule", "<module>", "Reloads a <module>", self.PRIV_ADMIN, ["rmod"])

    def on_command(self, target, nick, command, commandtext, mod, admin):

        if command == "permissions":
            return self.reply_notice(nick, "Permissions for {}: Administrator: {} - Moderator: {}"
                                           .format(nick, "yes" if admin else "no", "yes" if mod else "no"))

        if command == "ping" and not commandtext:  # Don't reply with params, might interfere with some bots 'ping' cmd
            return self.reply_target(target, nick, "Yes, yes. I am here.")

        if command == "commands":
            if not commandtext:
                return self.listCommands(nick, mod, admin)
            return self.listCommands(nick, mod, admin, commandtext)

        if command == "commandinfo":
            if not commandtext:
                return self.reply_notice(nick, "Usage: commandinfo <command>")
            return self.reply_notice(nick, self._conn.commandhelp.getCommandInfo(commandtext))

        if command == "help":
            if not commandtext:
                return self.listCommands(nick, mod, admin)

            return self.reply_notice(nick, self._conn.commandhelp.getCommandHelp(commandtext))

        if mod:
            if command == "join":
                if not commandtext:
                    return self.reply_notice(nick, "Usage: join <channels to join>")

                self._conn.join(commandtext)
                return self.reply_notice(nick, "Attempting to join: {}".format(commandtext.replace(",", ", ")))

            if command == "part":
                if not commandtext:
                    return self.reply_notice(nick, "Usage: part <channels to part>")

                self._conn.part(commandtext)
                return self.reply_notice(nick, "Attempting to part: {}".format(commandtext.replace(",", ", ")))

            if command == "nick":
                if not commandtext:
                    return self.reply_notice(nick, "Usage: nick <new nick>")

                self._conn.nick(commandtext)
                return self.reply_notice(nick, "Attempting to change name to: {}".format(commandtext))

            if command == "message":
                m = commandtext.split()

                if not commandtext or len(m) < 2:
                    return self.reply_target(target, "Usage: message <target> <message>")

                mess = " ".join(m[1:])
                targ = m[0]

                self.reply_target(targ, None, mess)
                return self.reply_target(target, nick, "Sent message '{}' to '{}'.".format(mess, targ))

            if command == "loadedmodules" or command == "modules" or command == "mod":
                return self.reply_notice(nick, "The following modules are loaded: {}"
                                               .format(str(self._conn.ModuleHandler.getLoadedModulesList())))

            if command == "availablemodules" or command == "amod":
                return self.reply_notice(nick, "The following modules are available: {}"
                                               .format(str(self._conn.ModuleHandler.getAvailableModulesList())))

            if admin:
                if command == "shutdown":
                    self._conn.force_quit = True
                    self._conn.quit("Shutdown requested by {}".format(nick))
                    return True

                if command == "rehash":
                    self.reply_target(target, nick, "Rehashing my configuration right now.")

                    # optional syntax parameter: "rehash reconnect"
                    if not commandtext or commandtext and commandtext.strip().lower() != "reconnect":
                        self._conn.rehash()
                    else:
                        self._conn.rehash(True)
                    return True

                if command == "loadmodule" or command == "lmod":
                    if not commandtext:
                        return self.reply_notice(nick, "Usage: loadmodule <modulename>")

                    module = commandtext
                    if not module.endswith(".py"):
                        module = "{}.py".format(module)

                    success = self._conn.ModuleHandler.load(module)

                    if success:
                        return self.reply_target(target, nick, "Successfully loaded module '{}'".format(module))

                    if module not in self._conn.ModuleHandler.getAvailableModulesList():
                        return self.reply_target(target, nick, "Failed to load module '{}', are you sure it exists?"
                                                               .format(module))
                    return self.reply_target(target, nick, "Failed to load module '{}'.".format(module))

                if command == "unloadmodule" or command == "umod":
                    if not commandtext:
                        return self.reply_notice(nick, "Usage: unloadmodule <modulename>")

                    module = commandtext
                    if not module.endswith(".py"):
                        module = "{}.py".format(module)

                    success = self._conn.ModuleHandler.unload(module)

                    if success:
                        return self.reply_target(target, nick, "Successfully unloaded module '{}'".format(module))

                    if module not in self._conn.ModuleHandler.getLoadedModulesList():
                        return self.reply_target(target, nick,
                                                 "Failed to unload module '{}', are you sure it is loaded?"
                                                 .format(module))
                    return self.reply_target(target, nick, "Failed to unload module '{}'.".format(module))

                if command == "reloadmodule" or command == "rmod":
                    if not commandtext:
                        return self.reply_notice(nick, "Usage: reloadmodule <modulename>")

                    module = commandtext
                    if not module.endswith(".py"):
                        module = "{}.py".format(module)

                    success = self._conn.ModuleHandler.reload(module)

                    if success:
                        return self.reply_target(target, nick, "Successfully reloaded module '{}'".format(module))

                    if module not in self._conn.ModuleHandler.getAvailableModulesList():
                        return self.reply_target(target, nick,
                                                 "Failed to reload module '{}', are you sure it exists and is loaded?"
                                                 .format(module))
                    return self.reply_target(target, nick, "Failed to reload module '{}'.".format(module))

                if command == "reconnect":
                    self.reply_target(target, nick, "Reconnecting to the network right now.")
                    self._conn.reconnect()
                    return True

        return False

    def listCommands(self, nick, mod, admin, module=None):
        cmds = self._conn.commandhelp.getCommands(mod, admin, module)
        if module:
            self.reply_notice(nick, "Listing commands from the module '{}'".format(module))
        else:
            self.reply_notice(nick, "Listing all available commands:")

        max_cmds = 15
        cmdlist = ""
        i = 0
        for cmd in sorted(cmds):
            i += 1
            cmdlist += ", " + cmd

            if i == max_cmds:
                self.reply_notice(nick, cmdlist[2:])
                cmdlist = ""
                i = 0

        if cmdlist:
            self.reply_notice(nick, cmdlist[2:])

        return True
