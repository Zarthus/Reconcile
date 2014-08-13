"""
WolframAlpha by Zarthus
Licensed under MIT

Perform Wolfram Alpha queries with a simple command,
This will require you to fill in the WolframAlpha API key in the configuration.
"""

from core import moduletemplate

import requests
import urllib.parse
import xml.etree.ElementTree as et
import time


class WolframAlpha(moduletemplate.BotModule):

    def on_module_load(self):
        self.requireApiKey("wolframalpha")

        self.register_command("wolframalpha", "<query>", "Look up <query> from the powerful computational knowledge " +
                                                         "engine Wolfram Alpha.", self.PRIV_NONE, ["wa", "wolfram"])

        self.last_request = int(time.time())

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "wolframalpha" or command == "wa" or command == "wolfram":
            if "wolframalpha" not in self.api_key:
                # The module would initially not be loaded if there is no API Key, but safety checks never hurt anyone.
                return self.notice(nick, "There is no API Key set for WolframAlpha, please ask the maintainer" +
                                         " to configure one to be set.")

            if not commandtext:
                return self.notice(nick, "Usage: wolframalpha <query>")

            if self.last_request > int(time.time()) + 5:
                timeleft = int(time.time()) + 5 - self.last_request

                return self.notice(nick, "This command is rate limited. Please try again in {} second{}."
                                         .format(timeleft, "s" if timeleft != 1 else ""))

            query_url = "http://www.wolframalpha.com/input/?i={}".format(urllib.parse.quote(commandtext))
            query_response = self.compute(commandtext)
            return self.message(target, nick, "{} - {}".format(query_response, query_url))
        return False

    def compute(self, query):
        if "wolframalpha" not in self.api_key:
            return "No API Key set"

        api_key = self.api_key["wolframalpha"]

        # Handle the request
        self.last_request = int(time.time())
        apidata = requests.get("http://api.wolframalpha.com/v2/query", params={"input": query, "appid": api_key})
        root = et.fromstring(apidata.text)

        if root.attrib["success"] == "false":
            return "WolframAlpha did not find any data. See the URL for alternative interpretations."

        title = ""

        for pod in root:
            if "id" in pod.attrib and pod.attrib["id"] == "Input":
                continue

            if "title" in pod.attrib:
                title = pod.attrib["title"]
                for subpod in pod:
                    for data in subpod:
                        if "title" in data.attrib:
                            return "{}: {}".format(title, data.attrib["title"])

        return "No data found"
