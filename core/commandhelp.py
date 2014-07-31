"""
commandhelp.py
Register and unregister commands to make CommandHelp generate a nice list of which commands are available.
"""


class CommandHelp:

    PRIV_NONE = "none"
    PRIV_MOD = "mod"
    PRIV_ADMIN = "admin"

    def __init__(self, logger, command_prefix):
        self.command_prefix = command_prefix
        self.commands = {}
        self.logger = logger

    def register(self, command, params, help, priv, aliases=None, module=None):
        command = command.lower()

        if command in self.commands:
            self.logger.error("Attempted to register command '{}' from {}, but it was already registered."
                              .format(command, module if module else "unknown"))
        self.commands[command] = {"name": command, "params": params, "help": help, "priv": priv, "aliases": aliases,
                                  "module": module}

    def unregister(self, command, silent=False):
        command = command.lower()

        if command in self.commands:
            self.logger.log("Unregistering command '{}'".format(command))
            self.commands = self.commands.pop(command)
        else:
            self.logger.notice_verbose("Attempted to unregister command '{}' but it was not registered.".
                                       format(command))

    def isCommand(self, command):
        command = command.lower()

        if command in self.commands:
            return True
        return False

    def getCommands(self, list_mod=False, list_admin=False, module=None, sort=False):
        cmds = []

        for cmd in self.commands:
            command = self.commands[cmd]

            if (command["priv"] == self.PRIV_NONE or
                    list_mod and command["priv"] == self.PRIV_MOD or
                    list_admin and command["priv"] == self.PRIV_ADMIN or
                    module and command["module"] and command["module"].lower() == module.lower()):
                cmds.append(command["name"])

        if sort:
            cmds = sorted(cmds)

        return cmds

    def getCommandHelp(self, command):
        command = command.lower()

        if command not in self.commands:
            return "The command '{}' is not in my help file.".format(command)

        privstring = ""
        aliasstring = ""
        cmdparams = ""

        if self.commands[command]["params"]:
            cmdparams = self.commands[command]["params"] + " "

        if self.commands[command]["priv"] == self.PRIV_MOD:
            privstring = " - moderator command"
        elif self.commands[command]["priv"] == self.PRIV_ADMIN:
            privstring = " - administrator command"

        if self.commands[command]["aliases"]:
            for alias in self.commands[command]["aliases"]:
                aliasstring += ", {}".format(alias)
            aliasstring = " - aliases: {}".format(aliasstring[2:])

        return "{}{} {}- {}{}{}".format(self.command_prefix, command, cmdparams, self.commands[command]["help"],
                                        aliasstring, privstring)

    def getCommandInfo(self, command):
        command = command.lower()

        if command not in self.commands:
            return "The command '{}' is not in my help file.".format(command)

        privstring = ""
        aliasstring = ""
        if self.commands[command]["priv"] == self.PRIV_MOD:
            privstring = "moderator privileges"
        elif self.commands[command]["priv"] == self.PRIV_ADMIN:
            privstring = "administrator privileges"
        else:
            privstring = "no privileges"

        if self.commands[command]["aliases"]:
            for alias in self.commands[command]["aliases"]:
                aliasstring += ", '{}'".format(alias)
            aliasstring = aliasstring[2:]

        if not aliasstring:
            aliasstring = "with no aliases"
        else:
            aliasstring = "with aliases {}".format(aliasstring)

        return ("The command '{}' originates from the module '{}', {} and requires {} to use."
                .format(command, self.commands[command]["module"], aliasstring, privstring))
