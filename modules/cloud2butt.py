"""
Cloud2Butt by Zarthus
Licensed under MIT

Replace cloud with butt!
"""

from core import moduletemplate

import re


class Cloud2Butt(moduletemplate.BotModule):

    def on_module_load(self):
        self.cloud_regex = re.compile("cloud", re.IGNORECASE)
        self.strip_nick = re.compile("[:,]")

        if "rate_limit_delay" not in self.module_data:
            self.module_data["rate_limit_delay"] = 60

        if "ignore_nicks" not in self.module_data:
            self.module_data["ignore_nicks"] = True

    def on_privmsg(self, target, nick, message):
        if not target.startswith("#"):
            return

        if "cloud" in message.lower():
            # If it is a name in the channel, we don't want to constantly "correct" it.
            if self.module_data["ignore_nicks"]:
                splitMsg = message.split()

                for word in splitMsg:
                    if "cloud" in word.lower():
                        strippedNick = self.strip_nick.sub("", word)
                        if self.isOn(strippedNick, target):
                            self.log_verbose("Ignoring replacement of nickname '{}'.".format(strippedNick))
                            return

            if self.ratelimit("cloud2butt"):
                butt = ""
                if "CLOUD" in message:
                    butt = "BUTT"
                elif "Cloud" in message:
                    butt = "Butt"
                else:
                    butt = "butt"

                self.message(target, nick, self.cloud_regex.sub(butt, message))
