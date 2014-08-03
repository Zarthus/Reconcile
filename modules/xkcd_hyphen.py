"""
hyphen.py by Zarthus
Licensed under MIT

This replaces sentences like "hey there ass man" with "hey there ass-man"
http://xkcd.com/37/
"""

from core import moduletemplate
import time


class XkcdHyphen(moduletemplate.BotModule):

    def on_module_load(self):
        self.ass_cooldown = time.time()

    def on_privmsg(self, target, nick, message):
        if time.time() + 10 > self.ass_cooldown:
            ass_next = False

            for word in message.split():
                if ass_next:
                    ass_next = False
                    assword = "ass-{}".format(word)
                    m = message.replace("-ass", "").replace(word, assword)
                    self.reply_target(target, nick, m)
                    self.ass_cooldown = time.time()
                    break

                if word.endswith("-ass"):
                    ass_next = True
