"""
Title by Zarthus
Licensed under MIT

Fetches titles from messages that seem to contain URLs.
"""

from core import moduletemplate

import lxml.html
import urllib.parse
import re
import requests


class Title(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("title", "<website>", "Get the title from <website>", self.PRIV_NONE, ["gettitle"])
        self.register_command("xkcd", "<id>", "Get information from the xkcd <id> specified", self.PRIV_NONE)

        self.last_title = None
        self.xkcdurl = re.compile(r"(https?:\/\/)?xkcd\.com\/[0-9]{1,5}\/?")

    def on_privmsg(self, target, nick, message):
        for word in message.split():
            if self.is_url(word):
                if self.xkcdurl.match(word):
                    info = self.get_xkcd_info(word)
                    if info:
                        self.reply_target(target, None, "({}) {}".format(nick, info), True)
                else:
                    title = self.get_title(word, True, True)
                    if title and title != self.last_title:
                        self.last_title = title
                        self.reply_target(target, None, "({}) {}".format(nick, title))

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "title" or command == "gettitle":
            if not commandtext:
                return self.reply_notice(nick, "Usage: title <website>")
            return self.reply_target(target, nick, self.get_title(commandtext, False))
        if command == "xkcd":
            if not commandtext or not commandtext.isdigit():
                return self.reply_notice(nick, "Usage: xkcd <id>")
            return self.reply_target(target, nick, self.get_xkcd_info("http://xkcd.com/{}/".format(commandtext)), True)
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
        return "'{}' at {}".format(title.strip(), urllib.parse.urlparse(url).netloc)

    def get_xkcd_info(self, url):
        if not url.endswith("/"):
            url = url + "/"

        json = None

        try:
            r = requests.get("{}info.0.json".format(url))
            r.raise_for_status()
            json = r.json
        except Exception as e:
            self.logger.notice("Failed to get xkcd '{}': {}".format(url, str(e)))
            return "Failed to get xkcd '{}' - {}".format(url, str(e))

        months = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }

        if "year" in json and "month" in json and "day" in json and "num" in json and "safe_title" in json:
            explainurl = "http://www.explainxkcd.com/{}".format(json["num"])

            return ("xkcd $(bold) {} $+ $(bold) : $(bold) {} $(bold) ({} {} {}) - Explained: {}"
                    .format(json["num"], json["safe_title"], json["day"], months[int(json["month"])], json["year"],
                            explainurl))
        return "Failed to get xkcd '{}'.".format(url)
