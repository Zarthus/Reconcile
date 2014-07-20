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
        self._conn = info["IrcConnection"]

        self.success = self._processCommand(command, commandtext)

    def _processCommand(self, command, commandtext):
        if command == "ping":
            self.reply_channel("Yes, hello {}!".format(self.nick))

    def reply_channel(self, message):
        self._conn.say(self.target, message)

    def reply_notice(self, message):
        self._conn.notice(self.nick, message)

    def getSuccess(self):
        return self.success
