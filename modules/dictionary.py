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

Dictionary by Zarthus
Licensed under MIT

This module spellchecks, and looks up words from a dictionary.
"""

from core import moduletemplate

import requests
import xml.etree.ElementTree as et


class Dictionary(moduletemplate.BotModule):

    def on_module_load(self):
        try:  # You may specify your own API key.
            self.requireApiKey("atd_spellcheck")
        except Exception:
            # Generate our own API Key.
            import hashlib
            uniquestr = bytes(self.network_name + self._conn.mnick + self._conn.altnick, "UTF-8")
            self.api_key["atd_spellcheck"] = hashlib.md5(uniquestr).hexdigest()

        self.register_command("spellcheck", "<word/sentence>",
                              "Check if <word/sentence> contains any grammatical errors, and provide suggestions to "
                              "correct those.",
                              self.PRIV_NONE, ["spell"])

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "spell" or command == "spellcheck":
            if not commandtext:
                return self.notice(nick, "Usage: spellcheck <word/sentence>")

            spellcheck = self.spell_check(commandtext)
            if spellcheck:
                if type(spellcheck) == dict:
                    spstr = ""
                    for item in spellcheck.items():
                        itemstr = ""
                        for listitem in item[1]:
                            itemstr = "{}, {}".format(itemstr, listitem)
                        itemstr = itemstr.lstrip(", ")
                        spstr = "{} | Suggestions for $(bold){}$(bold): {}".format(spstr, item[0], itemstr)
                    spstr = spstr.lstrip(" | ")

                    return self.message(target, nick, spstr, True)
                elif spellcheck == commandtext:
                    return self.message(target, nick, "This looks correct to me.")
                else:
                    return self.message(target, nick, spellcheck)
            return self.message(target, nick, "I don't have any suggestions.")

    def spell_check(self, check):
        api_url = "http://service.afterthedeadline.com/checkDocument"
        api_key = self.api_key["atd_spellcheck"]

        payload = {
            "key": api_key,
            "data": check
        }

        xml = None
        try:
            r = requests.post(api_url, data=payload)
            r.raise_for_status()

            xml = r.text
        except Exception as e:
            self.error("Spellcheck error: {}".format(str(e)))
            return "Could not check spelling: {}".format(str(e))

        retlist = {}
        root = et.fromstring(xml)
        for child in root:
            for subchild in child:
                if subchild.tag == "string":
                    curstr = subchild.text
                    retlist[subchild.text] = []
                if subchild.tag == "suggestions" and curstr:
                    for option in subchild:
                        retlist[curstr].append(option.text)
        return retlist
