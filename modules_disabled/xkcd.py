"""
The MIT License (MIT)

Copyright (c) 2014 - 2015 Jos "Zarthus" Ahrens and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

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
                        self.message(target, None, "({}) {}".format(nick, info), True)

    def get_xkcd_info(self, url, ret_boolean=False):
        if not url.endswith("/"):
            url = url + "/"

        json = None

        try:
            r = requests.get("{}info.0.json".format(url))
            r.raise_for_status()
            json = r.json()
        except Exception as e:
            self.warning("Failed to get xkcd '{}': {}".format(url, str(e)))
            return False if ret_boolean else "Failed to get xkcd '{}': {}".format(url, str(e))

        months = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }

        if "year" in json and "month" in json and "day" in json and "num" in json and "safe_title" in json:
            explainurl = "http://www.explainxkcd.com/{}".format(json["num"])

            return ("xkcd $(bold){}$(bold): $(bold){}$(bold) ({} {} {}) - Explained: {}"
                    .format(json["num"], json["safe_title"], json["day"], months[int(json["month"])], json["year"],
                            explainurl))
        return False if ret_boolean else "Failed to get xkcd '{}'.".format(url)
