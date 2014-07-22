"""
ExampleModule by Zarthus
Does things that you expect an Example to do.
"""

from core import moduletemplate


class Example(moduletemplate.BotModule):
    """Example Module class"""

    def on_command(self, channel, nick, command, commandtext, mod=False, admin=False):
        if command == "example":
            return self.reply_channel(channel, nick, "This is an example module command")

        if command == "nexample":
            return self.reply_notice(nick, "This is an example module command with a notice")

        return False

    def getAvailableCommands(self):
        return {
            "example": {
                "priv": "none",
                "help": "This is an example command"
            },

            "nexample": {
                "priv": "none",
                "help": "This is an example command with a notice response"
            }
        }
