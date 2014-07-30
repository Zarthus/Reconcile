"""
Title by Zarthus
Licensed under MIT

Fetches titles from messages that seem to contain URLs.
"""

from core import moduletemplate

import lxml.html
import urllib.parse


class Title(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("title", "<website>", "Get the title from <website>", self.PRIV_NONE, ["gettitle"])
        self.last_title = None

    def on_privmsg(self, target, nick, message):
        for word in message.split():
            if self.is_url(word):
                title = self.get_title(word, True, True)
                if title and title != self.last_title:
                    self.last_title = title
                    self.reply_target(target, None, "({}) {}".format(nick, title))

    def on_action(self, target, nick, action):
        for word in action.split():
            if self.is_url(word):
                title = self.get_title(word, True, True)
                if title and title != self.last_title:
                    self.last_title = title
                    self.reply_target(target, None, "({}) {}".format(nick, title))

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "title" or command == "gettitle":
            if not commandtext:
                return self.reply_notice(nick, "Usage: title <website>")
            return self.reply_target(target, nick, self.get_title(commandtext, False))

        return False

    def is_url(self, url):
        parsedurl = urllib.parse.urlparse(url)

        if parsedurl.netloc:
            return True
        return False

    def get_title(self, url, check_url=True, ret_false=False):
        if check_url and not self.is_url(url):
            return "'{}' is not a valid URL".format(url)

        fail_retry = False
        html = ""

        try:
            html = lxml.html.parse(url)
        except IOError:
            if not url.startswith("http"):
                fail_retry = True
        except Exception:
            pass

        if fail_retry:
            url = "http://" + url

            try:
                html = lxml.html.parse(url)
            except Exception:
                pass

        if not html:
            return "Failed to parse '{}'".format(url) if not ret_false else False

        title = ""
        try:
            title = html.find(".//title").text
        except Exception:
            pass

        if not len(title):
            return "Cannot find title for '{}'".format(url) if not ret_false else False
        return "'{}' at {}".format(self.html_decode(title.strip()), urllib.parse.urlparse(url).netloc)

    def html_decode(self, string):
        entities = {
            "&lt;": "<",
            "&gt;": ">",
            "&amp;": "&",
            "&quot;": "\"", "&#34;": "\"",
            "&#39;": "'"
        }

        for entity in entities.items():
            string = string.replace(entity[0], entity[1])

        return string
