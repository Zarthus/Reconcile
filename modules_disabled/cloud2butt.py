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
            if "irccloud.com" in message.lower():  # Ignore irccloud.com
                return

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
