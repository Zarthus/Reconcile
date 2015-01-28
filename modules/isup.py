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

isup.py by Zarthus
Licensed under MIT

isup - check if a website is up using isup.me and the bot itself
"""

from core import moduletemplate

import requests


class Isup(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("isup", "<website>", "Checks if <website> is up using isup.me", self.PRIV_NONE,
                              ["isdown"])

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "isup" or command == "isdown":
            if commandtext and " " not in commandtext:
                self.check_if_up(commandtext, target, nick)
            else:
                self.notice(nick, "Usage: isup <website> -- check if a website is up using isup.me")

            return True

        return False

    def check_if_up(self, url, target, nick):
        url = url.replace("https://", "").replace("http://", "")
        r = requests.get("http://isup.me/{}".format(url))

        isup = ""

        if "It's just you. " in r.text:
            isup = "$(green)up$(clear)"
        elif "It's not just you! " in r.text:
            isup = "$(red)down$(clear)"
        elif "doesn't look like a site on the interwho" in r.text:
            isup = "$(dgrey)an invalid website$(clear)"
        else:
            isup = "$(dgrey)unknown$(clear)"

        self.message(target, nick, "{} appears to be {}.".format(url, isup), True)
