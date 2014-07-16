"""
Zarthus <zarthus@zarth.us>
13 July, 2014.
"""

import json
import os
import sys

from tools import hostmask


class Config:
    """
    Parse the config in the root directory (config.json)
    and set variables to its appropriate values.
    """

    networks = {}
    api_keys = {}
    metadata = {}

    def __init__(self):
        self.load()

    def load(self):
        """Load the configuration -- called upon creation of the class"""
        file = "config.json"

        if os.path.isfile(file):
            print("config.json found! Attempting to load configuration..")
            try:
                config = json.load(open(file))

                self.networks = config["irc"]
                self.api_keys = config["api_keys"]
                self.metadata = config["metadata"]

                val = self._validate()
                print("Configuration successfully loaded. Networks: {}, Warnings: {}.".format(val[0], val[1]))
            except Exception as e:
                print("An error occured while loading config.json:\n{}".format(str(e)))
                sys.exit(1)
        else:
            print("Could not find configuration file config.json, did you configure the bot?")
            sys.exit(1)

    def getNetwork(self, network):
        return self.networks[network] if network in self.networks else None

    def getNetworkItem(self, network, item):
        return self.networks[network][item] if network in self.networks and item in self.networks[network] else None

    def getCommandPrefix(self, network):
        return self.networks[network]["command_prefix"] if network in self.networks else "!"

    def isAdministrator(self, network, address):
        if network in self.networks:
            for addr in self.networks[network]["administrators"]:
                if hostmask.match(address, addr):
                    return True

        return False

    def isModerator(self, network, hostmask):
        if network in self.networks:
            for addr in self.networks[network]["moderators"]:
                if hostmask.match(address, addr):
                    return True

        return self.isAdministrator(network, address)

    def getApiKey(self, api_name):
        return self.api_keys[api_name] if api_name in self.api_keys else None

    def getMetadata(self, item):
        return self.metadata[item] if item in self.metadata else None

    def getMaintainer(self):
        return self.metadata["bot_maintainer"] if "bot_maintainer" in self.metadata else "No maintainer found"

    def getVersion(self):
        return self.metadata["bot_version"] if "bot_version" in self.metadata else "Unknown"

    def getGithubURL(self):
        return self.metadata["github_url"] if "github_url" in self.metadata else "http://zarth.us"

    def getVerbose(self):
        return True if "verbose" in self.metadata and self.metadata["verbose"] else False

    def _validate(self, verbose=None):
        count = 0
        warnings = 0

        if not verbose:
            verbose = self.getVerbose()

        for network in self.networks:
            network_name = self.networks.keys()[count]

            self.networks[network_name]["id"] = count

            if not self.networks[network_name]["nick"]:
                # Todo: think of a name
                self.networks[network_name]["nick"] = "ok"
                print("'nick' was not configured in {} - default value assumed".format(network_name)) if verbose
                warnings += 1

            if not self.networks[network_name]["altnick"]:
                self.networks[network_name]["altnick"] = self.networks[network_name]["nick"] + "_"
                print("'altnick' was not configured in {} - default value assumed".format(network_name)) if verbose
                warnings += 1

            if not self.networks[network_name]["ident"]:
                self.networks[network_name]["ident"] = self.networks[network_name]["nick"]
                print("'ident' was not configured in {} - default value assumed".format(network_name)) if verbose
                warnings += 1

            if not self.networks[network_name]["realname"]:
                self.networks[network_name]["realname"] = self.networks[network_name]["nick"] + \
                    " (" + self.getGithubURL() + ")"
                print("'realname' was not configured in {} - default value assumed".format(network_name)) if verbose
                warnings += 1

            if not self.networks[network_name]["account"]:
                self.networks[network_name]["account"] = self.networks[network_name]["nick"]
                print("'account' was not configured in {} - 'nick' assumed".format(network_name)) if verbose
                warnings += 1

            if not self.networks[network_name]["command_prefix"]:
                self.networks[network_name]["command_prefix"] = "!"
                print("'command_prefix' was not configured in {} - '!' assumed".format(network_name)) if verbose
                warnings += 1

            count += 1

        return [count, warnings]
