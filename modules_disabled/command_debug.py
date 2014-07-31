"""
CmdDebug by Zarthus
Licensed under MIT

This plugin will notice all params sent by on_command to the user. 
Do not run this module if you're in spammy channels, use a test instance of the bot instead.
"""

from core import moduletemplate


class CmdDebug(moduletemplate.BotModule):
    def on_command(self, target, nick, command, commandtext, mod, admin):
        self.reply_notice(target, str([target, nick, command, commandtext, mod, admin]))