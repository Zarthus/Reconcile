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

        self.networks = {}
        self.api_keys = {}
        self.metadata = {}
        self.modules = {}

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

    def getLogTimestampFormat(self):
        return self.metadata["log_timestamp"] if "log_timestamp" in self.metadata else "%Y-%m-%d %H:%M:%S"

    def getDatabaseDir(self):
        if "db_dir" in self.metadata:
            self.metadata["db_dir"] = os.path.join(self.metadata["db_dir"])

            if not os.path.isdir(self.metadata["db_dir"]):
                os.mkdir(self.metadata["db_dir"])

            return self.metadata["db_dir"]
        else:
            self.metadata["db_dir"] = os.path.join("db")

            if not os.path.isdir("db"):
                os.mkdir("db")

            return "db"

    def getLogging(self):
        if "log_to_file" in self.metadata:
            if not self.metadata["log_to_file"]:
                return False
        return self.getLogDir()

    def getLogDir(self):
        if "log_dir" in self.metadata:
            self.metadata["log_dir"] = os.path.join(self.metadata["log_dir"])

            if not os.path.isdir(self.metadata["log_dir"]):
                os.mkdir(self.metadata["log_dir"])

            return self.metadata["log_dir"]
        else:
            self.metadata["log_dir"] = os.path.join("logs")

            if not os.path.isdir("logs"):
                os.mkdir("logs")

            return "logs"

    def getModuleData(self, module_name):
        return self.modules[module_name] if module_name in self.modules else None

    def parseAuthString(self, network_name):
        """
        Parse the auth_string - this configuration is quite verbose as there are many things that could be unwanted.

        This attempts to convert values wrapped in %<option>% to their respective networks array configuration.
        In the case you have custom network configurations, this method will also include that.

        The end product of the bot will only have auth_string in it.
        """
        nwname = network_name.lower()

        password = self.networks[network_name]["password"] if "password" in self.networks[network_name] else ""

        if not password:
            self.networks[network_name]["auth_string"] = False
            self.logger.log("No password set, cannot generate auth_string.")
            return
        elif "auth_string" not in self.networks[network_name]:
            if nwname == "quakenet":
                self.networks[network_name]["auth_string"] = "PRIVMSG Q@CServe.quakenet.org :AUTH %account% %password%"
            elif nwname == "espernet":
                self.networks[network_name]["auth_string"] = ("PRIVMSG NickServ@services.esper.net "
                                                              ":IDENTIFY %account% %password%")
            elif nwname == "freenode":
                self.networks[network_name]["auth_string"] = ("PRIVMSG NickServ@services. "
                                                              ":IDENTIFY %account% %password%")
            else:
                self.networks[network_name]["auth_string"] = "PRIVMSG NickServ :IDENTIFY %password%"

            self.logger.notice("No auth_string set. Assuming default value of: " +
                               self.networks[network_name]["auth_string"])
        else:
            self.logger.log("Attempting to parse auth_string: " + self.networks[network_name]["auth_string"])

        auth_string = self.networks[network_name]["auth_string"]
        replacements_count = 0
        replacements = []

        for key, value in self.networks[network_name].items():
            if not isinstance(key, str) or not isinstance(value, str):
                continue

            if key == "auth_string":
                continue

            if "%" + key + "%" in auth_string:
                auth_string = auth_string.replace("%" + key + "%", value)
                replacements_count += 1
                replacements.append(key)
                self.logger.log_verbose("Replacing '%" + key + "%' with value in configuration for auth_string.")

        if auth_string.count("%") / 2 >= 1:
            self.logger.notice("Still counting " + auth_string.count("%") +
                               " instances of the '%' character in auth_string after replacements.")
        if replacements_count > 0:
            self.logger.log("Replaced " + str(replacements_count) + " item" + ("s" if replacements_count > 1 else "") +
                            " in the auth_string.")
            self.logger.log_verbose("auth_string items replaced: " + str(replacements))
        else:
            self.logger.notice("Replaced " + replacements + " items in the auth_string.")

        if not auth_string.lower().startswith("privmsg "):
            self.logger.notice("auth_string does not start with 'PRIVMSG' - please verify your auth_string config.")

        self.networks[network_name]["auth_string"] = auth_string

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

            if "ipv4" in self.networks[network_name] and "ipv6" in self.networks[network_name]:
                if self.networks[network_name]["ipv4"] is self.networks[network_name]["ipv6"]:
                    self.logger.log_verbose("'ipv4' and 'ipv6' were configured in {} and the same, "
                                            "can only connect via one protocol.".format(network_name))
                    warnings += 1
            elif "ipv4" not in self.networks[network_name] and "ipv6" not in self.networks[network_name]:
                self.networks[network_name]["ipv4"] = True
            elif "ipv6" in self.networks[network_name] and "ipv4" not in self.networks[network_name]:
                self.networks[network_name]["ipv4"] = not self.networks[network_name]["ipv6"]

            if "nick" not in self.networks[network_name]:
                self.networks[network_name]["nick"] = "ReconcileBot"
                self.logger.log_verbose("'nick' was not configured in {} - default value assumed".format(network_name))
                warnings += 1

            if "altnick" not in self.networks[network_name]:
                self.networks[network_name]["altnick"] = self.networks[network_name]["nick"] + "_"
                self.logger.log_verbose("'altnick' was not configured in {} - default value assumed"
                                        .format(network_name))
                warnings += 1

            if "user" not in self.networks[network_name]:

                if "ident" not in self.networks[network_name]:
                    self.networks[network_name]["user"] = self.networks[network_name]["nick"]
                    self.logger.log_verbose("'user' was not configured in {} - default value assumed"
                                            .format(network_name))
                    warnings += 1
                else:
                    self.networks[network_name]["user"] = self.networks[network_name]["ident"]
                    self.logger.log_verbose("the 'ident' config option is deprecated and will be removed in "
                                            "future versions in {}, use 'user' instead."
                                            .format(network_name))

            if "realname" not in self.networks[network_name]:
                self.networks[network_name]["realname"] = self.networks[network_name]["nick"] + \
                    " (" + self.getGithubURL() + ")"
                self.logger.log_verbose("'realname' was not configured in {} - default value assumed"
                                        .format(network_name))
                warnings += 1

            if "channels" not in self.networks[network_name]:
                # Query the database to find out which channels to join.
                self.networks[network_name]["channels"] = cm.getListFromNetwork(network_name)

                chanlen = len(self.networks[network_name]["channels"])
                if chanlen == 0:
                    self.logger.log_verbose("Will not join any channels on {}.".format(network_name))
                else:
                    nicelist = None
                    for chan in self.networks[network_name]["channels"]:
                        if nicelist:
                            nicelist = ", {}".format(chan)
                        else:
                            nicelist = ": {}".format(chan)

                    self.logger.log_verbose("Will join {} channel{} on {}{}"
                                            .format(chanlen, "s" if chanlen != 1 else "",
                                                    network_name, nicelist))

            if "debug_chan" not in self.networks[network_name]:
                # Debug chan may be nothing at all, but we should still fill it in.
                self.networks[network_name]["debug_chan"] = False
            elif not self.networks[network_name]["debug_chan"].startswith("#"):
                self.networks[network_name]["debug_chan"] = False
                self.logger.log_verbose("'debug_chan' was set but wasn't a channel in {}.".format(network_name))
                warnings += 1
            else:
                dbgchan = self.networks[network_name]["debug_chan"]
                if dbgchan not in self.networks[network_name]["channels"]:
                    self.networks[network_name]["channels"].append(dbgchan)
                    self.logger.log_verbose("'debug_chan' ({}) was not in the channels to join list - added, in {}."
                                            .format(dbgchan, network_name))
                    cm.addForNetwork(network_name, dbgchan)

            if "account" not in self.networks[network_name]:
                self.networks[network_name]["account"] = self.networks[network_name]["nick"]
                self.logger.log_verbose("'account' was not configured in {} - 'nick' assumed".format(network_name))
                warnings += 1

            if "password" not in self.networks[network_name]:
                self.networks[network_name]["password"] = ""

            if "znc" not in self.networks[network_name]:
                self.networks[network_name]["znc"] = False

            if "command_prefix" not in self.networks[network_name]:
                self.networks[network_name]["command_prefix"] = "!"
                self.logger.log_verbose("'command_prefix' was not configured in {} - '!' assumed".format(network_name))
                warnings += 1

            if "invite_join" not in self.networks[network_name]:
                self.networks[network_name]["invite_join"] = False
                self.logger.log_verbose("'invite_join' was not configured in {} - False assumed".format(network_name))
                warnings += 1

            if "leave_empty_channels" not in self.networks[network_name]:
                self.networks[network_name]["leave_empty_channels"] = True

            if "modes" not in self.networks[network_name]:
                self.networks[network_name]["modes"] = None

            if "perform" not in self.networks[network_name]:
                self.networks[network_name]["perform"] = []

            if "moderators" not in self.networks[network_name]:
                self.networks[network_name]["administrators"] = []

            if "moderators" not in self.networks[network_name]:
                self.networks[network_name]["moderators"] = []

            if "disallowed_channels" not in self.networks[network_name]:
                self.networks[network_name]["disallowed_channels"] = []

            if "bindhost" not in self.networks[network_name]:
                self.networks[network_name]["bindhost"] = False

            if "ignorelist" not in self.networks[network_name]:
                self.networks[network_name]["ignorelist"] = []

            self.parseAuthString(network_name)
            count += 1

        return [count, warnings]
