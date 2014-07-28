"""
Google.py by Zarthus
Licensed under MIT

Look up data from google images and search.
"""

from core import moduletemplate
from tools import shorturl

import requests
import urllib.parse


class Google(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("google", "<search>", "Query google for <search> and return the first result.",
                              self.PRIV_NONE, ["search"])
        self.register_command("image", "<search>",
                              "Query google image search for <search> and return the first result.",
                              self.PRIV_NONE, ["gis", "imagesearch"])

    def on_command(self, target, nick, command, commandtext, mod=False, admin=False):
        if command == "google" or command == "search":
            if not commandtext:
                return self.reply_notice(nick, "Usage: google <search>")

            return self.reply_target(target, nick, self.google_search(commandtext))

        if command == "image" or command == "gis" or command == "imagesearch":
            if not commandtext:
                return self.reply_notice(nick, "Usage: image <search>")

            return self.reply_target(target, nick, self.google_image_search(commandtext))

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

            json = request.json
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

            json = request.json
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
                result = "'{}' at {} (Search: {})".format(json["responseData"]["results"][0]["titleNoFormatting"],
                                                          json["responseData"]["results"][0]["url"], gurl)
            except Exception:
                if gurl:
                    return ("The Google Image Search request failed because no results were found. (Search: {})"
                            .format(gurl))
                else:
                    return "The Google Image Search request failed because no results were found."

            if result:
                return result
        return "Google Image Search failed"
