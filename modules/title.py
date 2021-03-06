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

Title by Zarthus
Licensed under MIT

Fetches titles from messages that seem to contain URLs.
"""

from core import moduletemplate
from tools import urlparse
from tools import urltools

import re
import requests


class Title(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("title", "<website>", "Get the title from <website>", self.PRIV_NONE, ["gettitle"])
        self.register_command("xkcd", "<id>", "Get information from the xkcd <id> specified", self.PRIV_NONE)
        self.register_command("wikipedia", "<article> [language = en]", "Return information about <article>.",
                              self.PRIV_NONE, ["wiki"])

        self.last_title = None
        self.xkcdurl = re.compile(r"(https?:\/\/)?xkcd\.com\/[0-9]{1,5}\/?")
        self.wikipedia_url = re.compile(r"(https?:\/\/)?([a-z]{2}\.)?wikipedia\.[a-z]{1,3}\/wiki\/(.{1,32})")

    def on_privmsg(self, target, nick, message):
        urls = urlparse.Url.findAll(message)

        urls_found = 0
        for url in urls:
            if url.isUrl():
                urls_found += 1
                if urls_found > 3:
                    break

                if self.xkcdurl.match(url.getUrl()):
                    info = self.get_xkcd_info(url.getUrl(), True)
                    if info:
                        self.message(target, None, "({}) {}".format(nick, info), True)
                elif self.wikipedia_url.match(url.getUrl()):
                    match = self.wikipedia_url.match(url.getUrl())
                    groups = match.groups()
                    groups_len = len(groups)
                    article = groups[groups_len - 1]

                    language = ""
                    if groups_len > 1:
                        if len(groups[groups_len - 2]) == 3:
                            language = groups[groups_len - 2]

                    if not language:
                        language = "en"
                    if language.endswith("."):
                        language = language[:-1]

                    info = self.get_wiki_info(language, article, True)
                    if info:
                        self.message(target, None, "({}) {}".format(nick, info), True)
                else:
                    title = self.get_title(url.getUrl(), True)
                    if title and title != self.last_title:
                        self.last_title = title
                        self.message(target, None, ("({}) '{}' at {}.{}"
                                                    .format(nick, title, url.getDomain(), url.getTld())))

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "title" or command == "gettitle":
            if not commandtext:
                return self.notice(nick, "Usage: title <website>")
            return self.message(target, nick, self.get_title(commandtext, False))
        if command == "xkcd":
            if not commandtext or not commandtext.isdigit():
                return self.notice(nick, "Usage: xkcd <id>")
            return self.message(target, nick, self.get_xkcd_info("http://xkcd.com/{}/".format(commandtext)), True)
        if command == "wiki" or command == "wikipedia":
            if not commandtext:
                return self.notice(nick, "Usage: wiki <article> [language = en]")

            cmdtext = commandtext.split()
            article = cmdtext[0]

            language = "en"
            if len(cmdtext) > 1 and len(cmdtext[1]) == 2:
                language = cmdtext[1]

            return self.message(target, nick, self.get_wiki_info(language, article), True)
        return False

    def get_title(self, url, ret_false=False):
        return urltools.UrlTools.getTitle(url, ret_false)

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
            return False if ret_boolean else "Failed to get xkcd '{}' - {}".format(url, str(e))

        months = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }

        if "year" in json and "month" in json and "day" in json and "num" in json and "safe_title" in json:
            explainurl = "http://www.explainxkcd.com/{}".format(json["num"])

            return ("xkcd $(bold){}$(bold):$(bold) {}$(bold) ({} {} {}) - Explained: {}"
                    .format(json["num"], json["safe_title"], json["day"], months[int(json["month"])], json["year"],
                            explainurl))
        return False if ret_boolean else "Failed to get xkcd '{}'.".format(url)

    def get_wiki_info(self, language, article, ret_boolean=False):
        api_url = "http://{}.wikipedia.org/w/api.php".format(language)

        payload = {
            "format": "json",
            "action": "query",
            "titles": article,
            "prop": "extracts",
            "explaintext": "",
            "exlimit": 1,
            "exsentences": 4
        }

        json = None
        try:
            r = requests.get(api_url, params=payload)
            r.raise_for_status()
            json = r.json()
        except Exception as e:
            self.warning("Failed to retrieve wikipedia article '{}' - {}".format(article, str(e)))
            return False if ret_boolean else "Failed to retrieve wikipedia article '{}' - {}".format(article, str(e))

        if "query" in json and "pages" in json["query"]:
            data = json["query"]["pages"]
            pageid = list(data)[0]

            if pageid in data and "extract" in data[pageid] and "title" in data[pageid]:
                extract = data[pageid]["extract"].strip("\n")
                if len(extract) > 253:
                    extract = extract[:253] + "..."
                if not extract or extract.strip().startswith("==") and extract.strip().endswith("=="):
                    extract = "This wikipedia article does not yet exist."
                if extract.endswith("may refer to:"):  # will not work if we're not looking from en.wikipedia.org
                    return False if ret_boolean else "Information returned was not informative."

                return "Wikipedia article for $(bold){}$(bold): {}".format(data[pageid]["title"], extract)
            return False if ret_boolean else "Wikipedia returned no information."
        return False if ret_boolean else "Failed to retrieve wikipedia article '{}'.".format(article)
