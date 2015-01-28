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

Debug URLs by Zarthus
Licensed under MIT
"""

from core import moduletemplate
from tools import urlparse


class UrlDebug(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("isurl", "<url>", "Validate an URL through the Url class.", self.PRIV_ADMIN)
        self.register_command("findurl", "<url>", "Validate an URL through the Url class.", self.PRIV_ADMIN)
        self.register_command("dumpurl", "<url>", "Dump information about an URL", self.PRIV_ADMIN)
        self.register_command("urlstring", "<string>", "Validate multiple URLs through the Url class.",
                              self.PRIV_ADMIN)

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if admin:
            if command == "isurl":
                if not commandtext:
                    return self.notice(nick, "Usage: isurl <url>")

                link = commandtext

                urlclass = urlparse.Url(link)

                self.log(str(urlclass.getAsDict()))
                self.message(target, nick, ("{}: {}/{} certain, {}"
                                            .format(urlclass.getUrl(),
                                                    urlclass.getCertainty(),
                                                    urlclass.getMinCertainty(),
                                                    str(urlclass.getFactors()))))

                return True

            if command == "findurl":
                if not commandtext:
                    return self.notice(nick, "Usage: findurl <string>")

                u = urlparse.Url.find(commandtext)
                if not u:
                    return self.message(target, nick, "no matches")

                self.log(str(u.getAsDict()))

                self.message(target, nick, ("{}: {}/{} certain, {}"
                                            .format(u.getUrl(),
                                                    u.getCertainty(),
                                                    u.getMinCertainty(),
                                                    str(u.getFactors()))))
                return True

            if command == "dumpurl":
                if not commandtext:
                    return self.notice(nick, "Usage: dumpurl <string>")

                u = urlparse.Url.find(commandtext)
                if not u:
                    return self.message(target, nick, "no matches")

                self.message(target, nick, str(u.getAsDict()))
                return True

            if command == "urlstring":
                if not commandtext:
                    return self.notice(nick, "Usage: urlstring <string>")

                urllist = urlparse.Url.findAll(commandtext)
                if not urllist:
                    return self.message(target, nick, "no matches")

                for u in urllist:
                    self.log(str(u.getAsDict()))
                    self.message(target, nick, ("{}: {}/{} certain, {}"
                                                .format(u.getUrl(),
                                                        u.getCertainty(),
                                                        u.getMinCertainty(),
                                                        str(u.getFactors()))))
                return True

        return False
