"""
ColourDebug by Zarthus
Licensed under MIT

Send a message using the colour parser.
"""

from core import moduletemplate
from tools import formatter


class ColourDebug(moduletemplate.BotModule):
    def on_module_load(self):
        self.register_command("colours", None, "Return the same message formatted with the colour formatter.",
                              self.PRIV_ADMIN, ["colors"])
        self.register_command("strip", None, "Return the same message stripped of formatting-colours.",
                              self.PRIV_ADMIN)
        self.parser = formatter.IrcFormatter()

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if admin:
            if command == "colours" or command == "colors":
                if commandtext:
                    self.message(target, nick, commandtext, True)
                else:
                    self.message(target, nick, "This $(red, bold)is$(clear) a parsed$(bold) message$(clear).", True)
                return True

            if command == "strip":
                if commandtext:
                    self.message(target, nick, self.parser.strip(commandtext))
                else:
                    self.message(target, nick,
                                 self.parser.strip("This $(red, bold)is$(clear) a parsed$(bold) message$(clear)."))

        return False
