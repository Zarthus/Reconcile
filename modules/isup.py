"""
isup.py by Zarthus
Licensed under MIT

isup - check if a website is up using isup.me and the bot itself
"""

from core import moduletemplate

import requests


class Isup(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("isup", "<website>", "Checks if <website> is up using isup.me", self.PRIV_NONE,
                              ["isdown"])

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "isup" or command == "isdown":
            if commandtext and " " not in commandtext:
                self.check_if_up(commandtext, target, nick)
            else:
                self.reply_notice(nick, "Usage: isup <website> -- check if a website is up using isup.me")

            return True

        return False

    def check_if_up(self, url, target, nick):
        url = url.replace("https://", "").replace("http://", "")
        r = requests.get("http://isup.me/{}".format(url))

        isup = ""

        if "It's just you. " in r.text:
            isup = "$(green) up $+ $(clear)"
        elif "It's not just you! " in r.text:
            isup = "$(red) down $+ $(clear)"
        elif "doesn't look like a site on the interwho" in r.text:
            isup = "$(dgrey) an invalid website $+ $(clear)"
        else:
            isup = "$(dgrey) unknown $+ $(clear)"

        self.reply_target(target, nick, "{} appears to be {}.".format(url, isup), True)
