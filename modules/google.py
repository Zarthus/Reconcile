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

Google.py by Zarthus
Licensed under MIT

Look up data from google images and search.
"""

from core import moduletemplate
from tools import shorturl
from tools import urltools

import requests
import urllib.parse


class Google(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("google", "<search>", "Query google for <search> and return the first result.",
                              self.PRIV_NONE, ["search"])
        self.register_command("image", "<search>",
                              "Query google image search for <search> and return the first result.",
                              self.PRIV_NONE, ["gis", "imagesearch"])

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "google" or command == "search":
            if not commandtext:
                return self.notice(nick, "Usage: google <search>")

            return self.message(target, nick, self.google_search(commandtext))

        if command == "image" or command == "gis" or command == "imagesearch":
            if not commandtext:
                return self.notice(nick, "Usage: image <search>")

            return self.message(target, nick, self.google_image_search(commandtext))

        return False

    def google_search(self, search):
        url = "http://ajax.googleapis.com/ajax/services/search/web"
        payload = {
            "v": "1.0",
            "safe": "moderate",
            "q": search
        }
        json = ""

        try:
            request = requests.get(url, params=payload)
            request.raise_for_status()

            json = request.json()
        except Exception as e:
            return "Failed to look up query: {}".format(str(e))

        if "responseData" in json and "results" in json["responseData"]:
            gurl = False
            result = ""

            try:
                gurl = urltools.UrlTools.shorten("https://google.com/#q={}".format(urllib.parse.quote(search)))
            except Exception:
                gurl = "https://google.com/#q={}".format(urllib.parse.quote(search))

            try:
                result = "'{}' at {} (Search: {})".format(json["responseData"]["results"][0]["titleNoFormatting"],
                                                          json["responseData"]["results"][0]["url"], gurl)
            except Exception:
                if gurl:
                    return ("The Google Search request failed because no results were found. (Search: {})"
                            .format(gurl))
                else:
                    return "The Google Search request failed because no results were found."

            if result:
                return result
        return "Google Search failed"

    def google_image_search(self, search):
        url = "http://ajax.googleapis.com/ajax/services/search/images"
        payload = {
            "v": "1.0",
            "safe": "moderate",
            "q": search
        }
        json = ""

        try:
            request = requests.get(url, params=payload)
            request.raise_for_status()

            json = request.json()
        except Exception as e:
            return "Failed to look up query: {}".format(str(e))

        if "responseData" in json and "results" in json["responseData"]:
            gurl = False
            result = ""

            try:
                gurl = shorturl.ShortUrl.isgd("https://google.com/#q={}".format(urllib.parse.quote(search)))
            except Exception:
                gurl = "https://google.com/#q={}".format(urllib.parse.quote(search))

            try:
                title = self.html_decode(json["responseData"]["results"][0]["titleNoFormatting"])

                result = "'{}' at {} (Search: {})".format(title, json["responseData"]["results"][0]["url"], gurl)
            except Exception:
                if gurl:
                    return ("The Google Image Search request failed because no results were found. (Search: {})"
                            .format(gurl))
                else:
                    return "The Google Image Search request failed because no results were found."

            if result:
                return result
        return "Google Image Search failed"

    def html_decode(self, string):
        return urltools.UrlTools.htmlEntityDecode(string)
