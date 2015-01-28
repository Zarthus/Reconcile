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

urlshorten.py by Zarthus
Licensed under MIT

urlshorten - Shorten URLs using one of the many shortening services Reconcile supports.
"""

from core import moduletemplate
from tools import shorturl

import urllib.parse


class UrlShorten(moduletemplate.BotModule):

    def on_module_load(self):
        self.shorten_services = ["isgd", "googl", "scenesat"]

        self.register_command("urlshorten", "<url> [service]", "Shorten <URL> with [service]. " +
                              "Service can be: " + self.getAvailableServices(),
                              self.PRIV_NONE, ["shorten", "shorturl"])

    def on_command(self, target, nick, command, commandtext, mod, admin):

        if command in ["urlshorten", "shorten", "shorturl"]:
            if not commandtext:
                return self.notice(nick, "Usage: urlshorten <url> [service]")

            ct = commandtext.split()
            url = ct[0]

            if not self.is_url(url):
                return self.message(target, nick, "'{}' is not a valid URL.".format(url))

            if len(ct) > 1:
                service = ct[1]

                if not service or service.replace(".", "") not in self.shorten_services:
                    self.notice(nick, "Cannot find service '{}' - using {} instead."
                                      .format(service, self.getDefaultShortenService()))
                    service = self.getDefaultShortenService()
            else:
                service = self.getDefaultShortenService()

            service = service.replace(".", "")
            if service in self.shorten_services:
                return self.message(target, nick,
                                    ("{} was shortened to$(bold) {} $(bold)using {}'s shortening service."
                                     .format(url, self.shorten_url(url, service), service)), True)

            return self.message(target, nick, "Could not find the requested service.")

        return False

    def getAvailableServices(self):
        serv = ""

        for s in self.shorten_services:
            serv += s + ", "

        return serv[:-2]

    def getDefaultShortenService(self):
        return self.shorten_services[0]

    def is_url(self, url):
        parsedurl = urllib.parse.urlparse(url)

        if parsedurl.netloc:
            return True
        return False

    def shorten_url(self, url, service):
        if service not in self.shorten_services:
            return "Service was not in available services."

        api_key = None

        try:
            self.requireApiKey(service)
        except Exception:
            pass

        if service in self.api_key:
            api_key = self.api_key[service]

        return getattr(shorturl.ShortUrl, service)(url=url, api_key=api_key, logger=self.logger)
