"""
wikipedia.py by Zarthus
Licensed under MIT

Link extra information whenever a wikipedia article is linked.
This module in itself collides with title.py. It is not required to run both at the same time as title.py handles this.
"""

from core import moduletemplate

import re
import requests


class Wikipedia(moduletemplate.BotModule):

    def on_module_load(self):
        self.wikipedia_url = re.compile(r"(https?:\/\/)?([a-z]{2}\.)?wikipedia\.[a-z]{1,3}\/wiki\/(.{1,32})")

    def on_privmsg(self, target, nick, message):
        if self.wikipedia_url.search(message):
            for word in message.split():
                match = self.wikipedia_url.match(word)
                if match:
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

    def get_wiki_info(self, language, article, ret_boolean=False):
        api_url = "http://{}.wikipedia.org/w/api.php".format(language)

        payload = {
            "format": "json",
            "action": "query",
            "titles": article,
            "prop": "extracts",
            "explaintext": "",
            "exlimit": 1,
            "exsentences": 2
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
                extract = data[pageid]["extract"]
                if len(extract) > 253:
                    extract = extract[:253] + "..."
                return "Wikipedia article for $(bold){}$(bold): {}..".format(data[pageid]["title"], extract)
            return False if ret_boolean else "Wikipedia returned no information."
        return False if ret_boolean else "Failed to retrieve wikipedia article '{}'.".format(article)
