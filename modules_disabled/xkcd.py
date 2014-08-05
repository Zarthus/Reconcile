"""
xkcd.py by Zarthus
Licensed under MIT

Link extra information whenever a xkcd is linked.
This module in itself collides with title.py. It is not required to run both at the same time as title.py handles this.
"""

from core import moduletemplate

import re
import requests


class Xkcd(moduletemplate.BotModule):

    def on_module_load(self):
        self.xkcdurl = re.compile(r"(https?:\/\/)?xkcd\.com\/[0-9]{1,5}\/?")

    def on_privmsg(self, target, nick, message):
        if self.xkcdurl.search(message):
            for word in message.split():
                if self.xkcdurl.match(word):
                    info = self.get_xkcd_info(word)
                    if info:
                        self.reply_target(target, None, "({}) {}".format(nick, info), True)

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
            return False

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
        return False
