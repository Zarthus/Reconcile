"""
Substitutions by Zarthus
Licensed under MIT

Perform regex substitutions on recent messages in order to correct or improve them!
"""

from core import moduletemplate

import re


class Substitutions(moduletemplate.BotModule):

    def on_module_load(self):
        self.issubpattern = re.compile(r"[sS]/[^/]{1,64}/[^/]{1,64}[^ ]")
        self.previous_messages = {}

    def on_privmsg(self, channel, nick, message):
        if message.lower().startswith("s/") and self.issubpattern.match(message):
            msg = message.split("/")
            if len(msg) > 2 and len(msg) < 5:
                sub = self.substitute(channel, msg[1], msg[2])
                if sub:
                    if sub[0] == nick:
                        self.reply_channel(channel, None, "What {} meant to say: {}"
                                                          .format(nick, sub[1]))
                    else:
                        self.reply_channel(channel, None, "What {} thinks {} meant to say: {}"
                                                          .format(nick, sub[0], sub[1]))

        self.store(channel, "{} {}".format(nick, message))

    def store(self, channel, message):
        if channel in self.previous_messages:
            if len(self.previous_messages[channel]) > 10:
                self.previous_messages[channel].pop(0)
        else:
            self.previous_messages[channel] = []

        self.previous_messages[channel].append(message)

    def substitute(self, channel, search, replacement):
        if channel not in self.previous_messages:
            return False

        pattern = re.compile(search)

        msglist = self.previous_messages[channel]
        msglist.reverse()
        for msg in msglist:
            if pattern.search(msg):
                msg = msg.split(" ")
                nick = msg[0]
                msg = " ".join(msg[1:])
                sub = ""

                try:
                    sub = re.sub(search, replacement, msg)
                except Exception:
                    pass

                if sub:
                    return [nick, sub]
                break
        return False
