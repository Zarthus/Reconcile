"""
Command Handler:
All normal commands will be processed in here.
"""


class CommandHandler:
    def __init__(self, command, commandtext, info):
        self.nick = info["nick"]
        self.target = info["target"]
        self.admin = info["admin"]
        self.mod = info["mod"]
        self.command_prefix = info["command_prefix"]
        self._conn = info["IrcConnection"]

        self.success = self._processCommand(command, commandtext)

    def _processCommand(self, command, commandtext):
        """Processes default commands, not something a module should handle."""
        if command == "ping":
            return self.reply_channel("Yes, hello {}!".format(self.nick))

        if command == "permissions":
            return self.reply_notice("Permissions: Admin: {}, Moderator: {}"
                                     .format("yes" if self.admin else "no", "yes" if self.mod else "no"))

        if command == "commands":
            self.reply_notice("Commands I listen to: ping, permissions, commands, m:join, m:part, a:shutdown")
            return self.reply_notice("Command Prefix: {} - or address me by my name. ".format(self.command_prefix) +
                                     "- a: = admin only, m: = mod only")

        if self.mod:

            if command == "join":
                self._conn.join(commandtext)
                return self.reply_notice("Attempting to join: {}".format(commandtext))

            if command == "part":
                self._conn.part(commandtext)
                return self.reply_notice("Attempting to part: {}".format(commandtext))

            if self.admin:

                if command == "shutdown":
                    self._conn.quit("Requested shutdown by {}".format(self.nick))
                    raise KeyboardInterrupt  # TODO: A proper way to end the loop.

        return False

    def reply_channel(self, message):
        self._conn.say(self.target, message)
        return True

    def reply_notice(self, message):
        self._conn.notice(self.nick, message)
        return True

    def getSuccess(self):
        return self.success
