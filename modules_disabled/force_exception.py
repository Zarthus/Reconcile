"""
ForceException by Zarthus
Licensed under MIT

This module allows you to reproduce a traceback by raising an exception for debugging purposes.
"""

from core import moduletemplate


class ForceException(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("forceexception", None, "Force an Exception to occur.", self.PRIV_ADMIN)

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "forceexception" and admin:
            raise Exception("Requested exception by administrator {} in {}".format(nick, target))
            return True
        return False
