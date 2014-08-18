"""
Substitutions by Zarthus
Licensed under MIT

Perform regex substitutions on recent messages in order to correct or improve them!
"""

from core import moduletemplate

import re


class Substitution(moduletemplate.BotModule):

    def on_module_load(self):
        self.issubpattern = re.compile(r"[sS]/[^/]{1,64}/[^/]{1,64}[^ ]")
        self.previous_messages = {}

    def on_privmsg(self, target, nick, message):
        if message.lower().startswith("s/") and self.issubpattern.match(message):
            msg = message.split("/")
            if len(msg) > 2 and len(msg) < 5:
                sub = self.substitute(target, msg[1], msg[2])
                if sub:
                    if not sub[0] or sub[0] == nick:
                        self.message(target, None, "What {} meant to say: {}"
                                                   .format(nick, sub[1]))
                    else:
                        self.message(target, None, "What {} thinks {} meant to say: {}"
                                                   .format(nick, sub[0], sub[1]))
                    return True

        self.store(target, "{} {}".format(nick, message))

    def store(self, target, message):
        if target in self.previous_messages:
            if len(self.previous_messages[target]) > 10:
                self.previous_messages[target].pop(0)
        else:
            self.previous_messages[target] = []

        self.previous_messages[target].append(message)

    def substitute(self, target, search, replacement):
        if target not in self.previous_messages:
            return False

        msglist = self.previous_messages[target]
        msglist.reverse()
        invalid_regex = False
        errdata = None

        try:
            pattern = re.compile(search)
        except Exception as e:
            # More over to trying to just replace() it.
            invalid_regex = True
            self.logger.log_verbose("Substitute: Erroneous Regular Expression handled: {}".format(str(e)))

        for msg in msglist:
            if invalid_regex and search in msg or not invalid_regex and pattern.search(msg):
                msg = msg.split(" ")
                nick = msg[0]
                msg = " ".join(msg[1:])
                sub = ""

                if invalid_regex:
                    if msg.replace(search, replacement) != msg:
                        return [nick, msg.replace(search, replacement)]
                else:
                    try:
                        sub = re.sub(search, replacement, msg)
                    except Exception:
                        pass

                    if sub:
                        return [nick, sub]
                break
        return False
