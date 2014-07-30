"""
Zarthus <zarthus@zarth.us>
13 July, 2014.
"""

import json
import os
import sys

from core import channel
from tools import hostmask
from tools import logger


class Config:
    """
    Parse the config in the root directory (config.json)
    and set variables to its appropriate values.
    """

    networks = {}
    api_keys = {}
    metadata = {}
    modules = {}

    def __init__(self):
        self.logger = logger.Logger("Configuration")
        self.load()

    def rehash(self):
        self.logger.log("Rehashing configuration.")
        self.load()

    def load(self):
        """Load the configuration -- called upon creation of the class"""
        file = "config.json"

        if os.path.isfile(file):
            try:
                config = json.load(open(file))

                self.networks = config["irc"]
                self.api_keys = config["api_keys"]
                self.metadata = config["metadata"]
                self.modules = config["modules"]

                self.logger.setTimestamp(self.getTimestampFormat())
                val = self._validate()
                self.logger.log("Configuration successfully loaded. Networks: {}, Warnings: {}.\n"
                                .format(val[0], val[1]))
            except Exception as e:
                self.logger.error("An error occured while loading config.json:\n{}".format(str(e)))
                sys.exit(1)
        else:
            self.logger.error("Could not find configuration file config.json, did you configure the bot?")
            sys.exit(1)

    def getNetworks(self):
        return self.networks

    def getNetwork(self, network):
        return self.networks[network] if network in self.networks else None

    def getNetworkById(self, id):
        for network in self.networks:
            if network["id"] == id:
                return network

        return None

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

    def isModerator(self, network, address):
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

    def getTimestampFormat(self):
        return self.metadata["timestamp"] if "timestamp" in self.metadata else "%H:%M"

    def getDatabaseDir(self):
        if "db_dir" in self.metadata:
            if not self.metadata["db_dir"].endswith("/"):
                self.metadata["db_dir"] + "/"

            if not os.path.isdir(self.metadata["db_dir"]):
                os.mkdir(self.metadata["db_dir"])

            return self.metadata["db_dir"]
        else:
            if not os.path.isdir("db/"):
                os.mkdir("db/")

            return "db/"

    def getModuleData(self, module_name):
        return self.modules[module_name] if module_name in self.modules else None

    def _validate(self, verbose=None):
        count = 0
        warnings = 0
        cm = channel.ChannelManager(self.getDatabaseDir(), self.logger)

        if not verbose:
            verbose = self.logger.setVerbose(self.getVerbose())

        for network in self.networks:
            network_name = list(self.networks.keys())[count]

            self.networks[network_name]["id"] = count

            if "network_name" not in self.networks[network_name]:
                self.networks[network_name]["network_name"] = network_name

            if "nick" not in self.networks[network_name]:
                self.networks[network_name]["nick"] = "ReconcileBot"
                self.logger.log_verbose("'nick' was not configured in {} - default value assumed".format(network_name))
                warnings += 1

            if "altnick" not in self.networks[network_name]:
                self.networks[network_name]["altnick"] = self.networks[network_name]["nick"] + "_"
                self.logger.log_verbose("'altnick' was not configured in {} - default value assumed"
                                        .format(network_name))
                warnings += 1

            if "ident" not in self.networks[network_name]:
                self.networks[network_name]["ident"] = self.networks[network_name]["nick"]
                self.logger.log_verbose("'ident' was not configured in {} - default value assumed"
                                        .format(network_name))
                warnings += 1

            if "realname" not in self.networks[network_name]:
                self.networks[network_name]["realname"] = self.networks[network_name]["nick"] + \
                    " (" + self.getGithubURL() + ")"
                self.logger.log_verbose("'realname' was not configured in {} - default value assumed"
                                        .format(network_name))
                warnings += 1

            if "channels" not in self.networks[network_name]:
                # Query the database to find out which channels to join.
                self.networks[network_name]["channels"] = cm.getListFromNetwork(network_name)
                self.logger.log_verbose("Will join {} channels on {}: {}"
                                        .format(len(self.networks[network_name]["channels"]),
                                                network_name, self.networks[network_name]["channels"]))

            if "account" not in self.networks[network_name]:
                self.networks[network_name]["account"] = self.networks[network_name]["nick"]
                self.logger.log_verbose("'account' was not configured in {} - 'nick' assumed".format(network_name))
                warnings += 1

            if "password" not in self.networks[network_name]:
                self.networks[network_name]["password"] = ""

            if "command_prefix" not in self.networks[network_name]:
                self.networks[network_name]["command_prefix"] = "!"
                self.logger.log_verbose("'command_prefix' was not configured in {} - '!' assumed".format(network_name))
                warnings += 1

            if "invite_join" not in self.networks[network_name]:
                self.networks[network_name]["invite_join"] = False
                self.logger.log_verbose("'invite_join' was not configured in {} - False assumed".format(network_name))
                warnings += 1

            if "moderators" not in self.networks[network_name]:
                self.networks[network_name]["administrators"] = []

            if "moderators" not in self.networks[network_name]:
                self.networks[network_name]["moderators"] = []

            count += 1

        return [count, warnings]
