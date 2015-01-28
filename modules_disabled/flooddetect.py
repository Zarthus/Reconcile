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

FloodDetect by Zarthus
Licensed under MIT

This is a module that requires the bot to have OP in a channel.
It detects based on how often the user sends messages if they should be warned.

Note this however: This is not supposed to be a replacement for channel ops, it's just there to keep
control in a channel with large amounts of chatting.

The banmasks set are ineffecient and are not meant to go against ban evasion, they are supposed to give channel
ops the time to investigate the situation without some user wrecking havoc on the channel.

This module also unbans every ban the bot set on a purge.

It requires a lot of configuration, but the default values are generally fine. Ensure at LEAST "channels" is set.

Config options (in config.json):
 channels: string, Channels (, separated) to detect by default (nothing will happen if the bot is not in them)
 max_warnings: integer, number of warnings until nothing will happen (often equals a kickban or op supervision after)
 message_interval: integer, when a message expires and no longer counts towards the .. ->
 message_max_per_interval: integer, number of messages you can send before a warning is added.
 report_channel: string, much like "debug_chan", reports useful information to this channel (command uses, warnings).
 expiry_seconds: integer, Every expiry_seconds the bot will purge the storage, resetting warnings, and removing bans.

Additionally, code-wise, if you need something more specific from the module. You can edit self.actions in
on_module_load(). This includes writing your own actions, and adjusting the settings to see what works best for your
channel.

Known Issues:
 Channels with a ':' in them are not supported by the banlist. To fix this, manually adjust the code to use a different
 delimiter
"""

from core import moduletemplate
from tools import duration

import time
import math


class FloodDetect(moduletemplate.BotModule):

    def on_module_load(self):
        self.flood_detect = {}
        self.last_purge = int(time.time())
        self.banlist = []
        self.cdelim = ":"  # change this if you use channels with a colon in it, short for channel delimiter

        """
        Example of a flood detection dict

        self.flood_detect = {
            "channel": {
                "nick": {
                    "messages": [1421885807],
                    "warnings": 0
                }
            }
        }
        """

        self.register_command("fdsettings", None, "Display the current flood detect settings.", self.PRIV_NONE)
        self.register_command("fdpurge", None, "Purge all flood data for channel (requires OP or bot moderator).",
                              self.PRIV_NONE)
        self.register_command("fdpurgenick", "<nick>",
                              "Purge all flood data for channel for <nick> (requires OP or bot moderator).",
                              self.PRIV_NONE)
        self.register_command("fdinfo", "<nick>",
                              "Retrieve flood data information about <nick> (requires OP or bot moderator).",
                              self.PRIV_NONE)
        self.register_command("fdenable", "<#channel>", "Temporarily Enable flood detection for <#channel>.",
                              self.PRIV_MOD)
        self.register_command("fddisable", "<#channel>", "Temporarily Disable flood detection for <#channel>.",
                              self.PRIV_MOD)
        self.register_command("fdchans", None, "List channels flood detection is enabled in.", self.PRIV_MOD)

        if "channels" not in self.module_data or not self.module_data["channels"]:
            raise Exception("This module is not configured properly, no channels to protect from flooding set.")
        else:
            self.channels = self.module_data["channels"].replace(" ", "").split(",")

        if "max_warnings" not in self.module_data:
            self.module_data["max_warnings"] = 5

        if "message_interval" not in self.module_data:
            self.module_data["message_interval"] = 15
        if "message_max_per_interval" not in self.module_data:
            self.module_data["message_max_per_interval"] = 8

        if "expiry_seconds" not in self.module_data:
            self.expiry = 7200
        else:
            try:
                self.expiry = int(self.module_data["expiry_seconds"])
            except Exception:
                self.expiry = 7200
                self.log("Expiry was not a number, defaulting to 2 hours (7200 sec)")

        # Supported actions: private_message, message, kick, kickban
        self.actions = {
            "message": int(self.getWarnMaxCount() / 2 - 1),
            "kick": math.ceil(self.getWarnMaxCount() / 2),
            "kickban": self.getWarnMaxCount()
        }

        if self.actions["message"] < 1:
            self.actions["message"] = 1
        if self.actions["kickban"] == self.actions["kick"]:
            self.actions["kick"] -= 1

    def createDict(self, channel, nick):
        self.purge()  # Check if we should purge the data we gathered and start anew.

        if channel not in self.flood_detect:
            self.flood_detect[channel] = {}

        if nick.lower() not in self.flood_detect[channel]:
            self.flood_detect[channel][nick.lower()] = {
                "warnings": 0,
                "messages": []
            }

    def getActionForWarnCount(self, warncount):
        for k, v in self.actions.items():
            if warncount == v:
                return k

        return None

    def addWarn(self, channel, nick):
        self.createDict(channel, nick)
        self.flood_detect[channel][nick.lower()]["warnings"] += 1
        self.flood_detect[channel][nick.lower()]["messages"] = []

        warnings = self.flood_detect[channel][nick.lower()]["warnings"]
        action = self.getActionForWarnCount(warnings)
        if action:
            mi = self.module_data["message_interval"]
            mmpi = self.module_data["message_max_per_interval"]
            action = action.upper()

            if action == "PRIVATE_MESSAGE":
                self.message(nick, None, ("You have been issued a warning for flooding in {}. Please cease your "
                                          "activities before further action will be taken.").format(channel))
            elif action == "MESSAGE":
                self.message(channel, nick, "Please cease flooding, further action will be taken if you continue.")
            elif action == "KICK":
                self.message(nick, None, "You have been kicked from {} for flooding. Please cease your activities."
                                         .format(channel))
                self._conn.send_raw("KICK {} {} :Repeated Flooding ({} messages in {} seconds)"
                                    .format(channel, nick, mi, mmpi))
            elif action == "KICKBAN":
                self.message(nick, None, "You have been banned from {} for flooding. Please contact a channel OP."
                                         .format(channel))
                self.mode(channel, "+b {}!*@*".format(nick))
                self.banlist.append("{}{}{}!*@*".format(channel.replace(self.cdelim, ""), self.cdelim, nick))
                self._conn.send_raw("KICK {} {} :Repeated Flooding ({} messages in {} seconds)"
                                    .format(channel, nick, mi, mmpi))
            else:
                action += " (unknown action)"
        else:
            action = "No action taken"

        self.on_warning(action.replace("_", " "), channel, nick)

    def getWarnMaxCount(self):
        return self.module_data["max_warnings"]

    def getWarningsFor(self, channel, nick):
        self.createDict(channel, nick)
        return self.flood_detect[channel][nick.lower()]["warnings"]

    def on_warning(self, action, channel, nick):
        warnmessage = ("[Report] {} for {}/{} ({}/{} warnings)".format(action, channel, nick,
                                                                       self.getWarningsFor(channel, nick),
                                                                       self.getWarnMaxCount()))
        self.logreport(warnmessage)

    def purge(self, force=False):
        if force or int(time.time()) >= self.last_purge + self.expiry:
            self.flood_detect = {}
            self.last_purge = int(time.time())

            banstring = ""
            last_target = ""
            iter = 0
            for bans in self.banlist:
                ban = bans.split(self.cdelim)
                current_target = ban[0]
                banstring += ban[1] + " "
                iter += 1

                if iter == 4 or last_target != current_target:
                    iter = 0
                    self.mode(current_target, "-" + ("b" * iter) + " " + banstring.strip())

                last_target = current_target
                banstring = ""

            self.banlist = []

            self.log("Purged Flood Detection storage.")

    def addMessage(self, channel, nick):
        self.createDict(channel, nick)
        self.checkIntervalFor(channel, nick)
        self.flood_detect[channel][nick.lower()]["messages"].append(int(time.time()))

        if len(self.flood_detect[channel][nick.lower()]["messages"]) > self.module_data["message_max_per_interval"]:
            self.addWarn(channel, nick)

    def logreport(self, message):
        if "report_channel" in self.module_data:
            self.message(self.module_data["report_channel"], None, message)
        self.log(message)

    def checkIntervalFor(self, channel, nick):
        t = int(time.time()) - self.module_data["message_interval"]
        rem = []

        for ts in self.flood_detect[channel][nick.lower()]["messages"]:
            if t > ts:
                rem.append(ts)

        for rts in rem:
            self.flood_detect[channel][nick.lower()]["messages"].remove(rts)

    def on_connect(self):
        if "report_channel" in self.module_data:
            self._conn.join_channel(self.module_data["report_channel"])
        if self.channels:
            self._conn.join_channel(self.channels.join(","))

    def on_privmsg(self, target, nick, message):
        for chan in self.channels:
            if target == chan:
                self.addMessage(target, nick)

    def on_action(self, target, nick, action):
        for chan in self.channels:
            if target == chan:
                self.addMessage(target, nick)

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if target.startswith("#"):
            if command == "fdsettings":
                purdur = duration.timesincetimestamp(self.last_purge)
                expdur = duration.timesincetimestamp(time.time() - self.expiry)
                return self.notice(nick, ("Max Warns: {}, Interval: {}, Messages Per Interval: {}, Expiry: {} ({}), "
                                          "Last Purge: {} ago".format(self.getWarnMaxCount(),
                                                                      self.module_data["message_interval"],
                                                                      self.module_data["message_max_per_interval"],
                                                                      expdur, self.expiry, purdur)))

            if command == "fdinfo":
                if not self.isOp(nick, target) and not mod:
                    return self.notice(nick, "Sorry, you need to be an OP to use this command.")
                if target not in self.module_data["channels"]:
                    return self.notice(nick, "You need to use this command in a flood detecting channel.")
                if not commandtext:
                    return self.notice(nick, "Usage: fdinfo <nick>")
                if commandtext.lower() not in self.flood_detect[target]:
                    return self.message(target, nick, "No data found on user.")

                self.logreport("fdinfo on {} requested by {} in {}.".format(commandtext, nick, target))
                return self.notice(nick, str(self.flood_detect[target][commandtext.lower()]))

            if command == "fdpurge":
                if not self.isOp(nick, target) and not mod:
                    return self.notice(nick, "Sorry, you need to be an OP to use this command.")
                if target not in self.module_data["channels"]:
                    return self.notice(nick, "You need to use this command in a flood detecting channel.")

                self.logreport("fdpurge on {} requested by {} in {}.".format(commandtext, nick, target))
                self.flood_detect[target] = {}
                return self.notice(nick, "Data purged for channel.")

            if command == "fdpurgenick":
                if not self.isOp(nick, target) and not mod:
                    return self.notice(nick, "Sorry, you need to be an OP to use this command.")
                if target not in self.module_data["channels"]:
                    return self.notice(nick, "You need to use this command in a flood detecting channel.")
                if not commandtext:
                    return self.notice(nick, "Usage: fdpurgenick <nick>")
                if target not in self.flood_detect:
                    self.createDict(target, commandtext)

                self.logreport("fdpurgenick on {} requested by {} in {}.".format(commandtext, nick, target))
                self.flood_detect[target][nick.lower()] = {"messages": [], "warnings": 0}
                return self.notice(nick, "Data purged for nick '{}' on '{}'.".format(commandtext, target))

            if mod:
                if command == "fdchans":
                    if self.module_data["channels"]:
                        return self.message(target, nick, "I am checking for flooding in: {}"
                                                          .format(self.module_data["channels"]))

                if command == "fddisable":
                    if target in self.module_data["channels"]:
                        newchannels = self.module_data["channels"].replace(target, "").replace(",,", ",").rstrip(",")
                        self.module_data["channels"] = newchannels
                        self.channels = self.module_data["channels"].replace(" ", "").split(",")
                        self.logreport("Disabled Flood Detection in {} (requested by {})".format(target, nick))
                        return self.message(target, nick, "Flood Detection disabled for {}.".format(target))
                    return self.message(target, nick, "Flood Detection not enabled in channel.")

                if command == "fdenable":
                    if target not in self.module_data["channels"]:
                        self.module_data["channels"] += "," + target
                        self.channels = self.module_data["channels"].replace(" ", "").split(",")
                        self.logreport("Enabled Flood Detection in {} (requested by {})".format(target, nick))
                        return self.message(target, nick, "Flood Detection enabled for {}.".format(target))
                    return self.message(target, nick, "Flood Detection already enabled in channel.")

        return False
