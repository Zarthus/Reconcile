"""
isup.py by Zarthus
Licensed under MIT

isup - check if a website is up using isup.me and the bot itself
"""

from core import moduletemplate
from tools import formatter

import requests


class Isup(moduletemplate.BotModule):
    """checks if a website is up or not"""

    def on_module_load(self):
        self.colformat = formatter.IrcFormatter()

    def on_command(self, channel, nick, command, commandtext, mod=False, admin=False):
        if command == "isup" or command == "isdown":
            if commandtext and " " not in commandtext:
                self.check_if_up(commandtext, channel, nick)
            else:
                self.reply_notice(nick, "Usage: isup <website>")

            return True

        return False

    def check_if_up(self, url, channel, nick):
        url = url.replace("https://", "").replace("http://", "")
        r = requests.get("http://isup.me/{}".format(url))

        isup = ""

        if "just you" in r.text:
            isup = "$(green) up $+ $(clear)"
        else:
            isup = "$(red) down $+ $(clear)"

        self.reply_channel(channel, nick, "{} appears to be {}.".format(url, self.colformat.parse(isup)))

    def getAvailableCommands(self):
        return {
            "isup": {
                "priv": "none",
                "help": "check if a website is up"
            }
        }
