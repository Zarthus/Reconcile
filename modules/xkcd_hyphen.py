"""
xkcd_hyphen.py by Zarthus
Licensed under MIT

This replaces sentences like "That's a sweet-ass car" with "That's a sweet ass-car"
http://xkcd.com/37/
"""

from core import moduletemplate


class XkcdHyphen(moduletemplate.BotModule):

    def on_module_load(self):
        if "rate_limit_delay" not in self.module_data:
            self.module_data["rate_limit_delay"] = 10

    def on_privmsg(self, target, nick, message):
        if self.ratelimit("xkcdhyphen_privmsg"):
            if not self.module_data or "full_sentence" in self.module_data and self.module_data["full_sentence"]:
                self.parse_full(target, nick, message)
            else:
                self.parse_partially(target, nick, message)

    def parse_full(self, target, nick, message):
        """This returns the entire sentence, 'that's a sweet ass-car'."""
        ass_next = False

        for word in message.split():
            if ass_next:
                assword = "ass-{}".format(word)
                m = message.replace("-ass", "").replace(word, assword)
                self.message(target, nick, m)
                break

            if word.endswith("-ass"):
                ass_next = True

    def parse_partially(self, target, nick, message):
        """This returns only the 'sweet ass-car' part of the message."""
        ass_next = False

        for word in message.split():
            if ass_next:
                m = "{} ass-{}".format(ass_next, word)
                self.message(target, nick, m)
                break

            if word.endswith("-ass"):
                ass_next = word.replace("-ass", "")
