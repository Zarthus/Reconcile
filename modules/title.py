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
        self.register_command("wikipedia", "<article> [language = en]", "Return information about <article>.",
                              self.PRIV_NONE, ["wiki"])

        self.last_title = None
        self.xkcdurl = re.compile(r"(https?:\/\/)?xkcd\.com\/[0-9]{1,5}\/?")
        self.wikipedia_url = re.compile(r"(https?:\/\/)?([a-z]{2}\.)?wikipedia\.[a-z]{1,3}\/wiki\/(.{1,32})")

    def on_privmsg(self, target, nick, message):
        for word in message.split():
            if self.is_url(word):
                if self.xkcdurl.match(word):
                    info = self.get_xkcd_info(word, True)
                    if info:
                        self.message(target, None, "({}) {}".format(nick, info), True)
                elif self.wikipedia_url.match(word):
                    match = self.wikipedia_url.match(word)
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
                    title = self.get_title(word, True, True)
                    if title and title != self.last_title:
                        self.last_title = title
                        self.message(target, None, "({}) {}".format(nick, title))

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

    def get_xkcd_info(self, url, ret_boolean=False):
        if not url.endswith("/"):
            url = url + "/"

        json = None

        try:
            r = requests.get("{}info.0.json".format(url))
            r.raise_for_status()
            json = r.json
        except Exception as e:
            self.logger.notice("Failed to get xkcd '{}': {}".format(url, str(e)))
            return False if ret_boolean else "Failed to get xkcd '{}' - {}".format(url, str(e))

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
            json = r.json
        except Exception as e:
            self.logger.notice("Failed to retrieve wikipedia article '{}' - {}".format(article, str(e)))
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

                return "Wikipedia article for $(bold) {} $+ $(bold) : {}".format(data[pageid]["title"],
                                                                                 extract)
            return False if ret_boolean else "Wikipedia returned no information."
        return False if ret_boolean else "Failed to retrieve wikipedia article '{}'.".format(article)
