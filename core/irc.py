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

IRC class for irc connections
"""

import socket
import ssl
import time
import re
import traceback
import queue
import threading

from core import channel
from core import module
from core import commandhelp
from core import ratelimit
from tools import validator
from tools import formatter
from tools import logger
from tools import paste
from tools import banmask


class IrcConnection(threading.Thread):
    def __init__(self, network, config, modules=None):
        self.running = True
        self.connected = False
        self.shutdownRequested = False

        self.network = network
        self.config = config

        threading.Thread.__init__(self)
        self.start()

    def run(self):
        self.loadNetworkVariables()
        self._loadModules()

        self.numeric_regex = re.compile(":.* [0-9]{3}")

        self.connect()
        while self.running:
            try:
                self.readBuffer()
            except KeyboardInterrupt:
                self.shutdownRequested = True
            except OSError:
                self.logger.log("OSError caught. Automatically terminating...")
                self.running = False
            except Exception as e:
                if int(time.time()) > self.time_error_per_minute + 60:
                    self.time_error_per_minute = int(time.time())
                    self.errors_per_minute = 0

                self.errors_per_minute += 1

                if self.errors_per_minute > 25:
                    self.running = False
                    self.quit("Too many errors per minute, exiting.")
                else:
                    traceback.print_exc()
                    tb = traceback.format_exc()

                    if self.debug_chan:
                        gist = paste.Paste.gist("Traceback for {} on {} at {}".format(self.currentnick,
                                                self.network_name,
                                                time.strftime(self.config.getMetadata("timestamp"))),
                                                tb, "traceback.py", False, self.logger)
                        self.debug("An exception has occured and has been logged: {} | {}".format(gist, str(e)))
        self.connected = False

    def readBuffer(self):
        buff = self.socket.recv(4096)
        lines = buff.decode("utf-8").split("\n")
        for data in lines:
            data = str(data).strip()

            if not data:
                continue

            words = data.split()

            if len(words) > 1:
                if words[0] == "PING":
                    # Reply to PING
                    self.send_raw("PONG " + words[1])
                    continue

                if self.numeric_regex.match(" ".join(words[:2])):
                    # Check if a server numeric is sent, and handle it appropriately.
                    if self.on_numeric(int(words[1]), data):
                        # _processIrcNumeric returns true if we need to continue, false if we don't
                        continue

                if self.isEvent(words[1]):
                    # Most(?) events share the following syntax:
                    # :nick!user@host EVENT target [[:]message/params]

                    uinfo = words[0][1:]
                    event = words[1]
                    target = words[2]
                    params = words[3:] if len(words) > 3 else None

                    self.processEvent(uinfo, event, target, params)

    def rehash(self, reconnect=False):
        self.config.rehash()
        self.ratelimiter.stop()
        self.loadNetworkVariables(self.config.getNetwork(self.network_name), self.currentnick)
        self.ratelimiter.start()
        self.ModuleHandler.unloadAll()
        self._loadModules()

        if reconnect:
            self.reconnect()
        else:
            if self.currentnick != self.mnick:
                self.nick(self.mnick)

        self.logger.log("Rehash completed.")

    def send_raw(self, data):
        self.socket.send(bytes(data + "\r\n", "utf-8"))

    def debug(self, message, format=False):
        self.logger.debug(message)

        if self.debug_chan:
            self.say(self.debug_chan, message, format)

    def say(self, target, message, format=False):
        """Queue a PRIVMG to the ratelimiter."""
        self.queue_privmsg.put([target, message, format], True)

    def notice(self, target, notice, format=False):
        """Queue a NOTICE to the ratelimiter."""
        self.queue_notice.put([target, notice, format], True)

    def action(self, target, action, format=False):
        """
        Sends a CTCP ACTION to target
        With formatting enabled, we will attempt to parse the contents through the IrcFormatter class.
        """

        if not format:
            self.logger.log("Sending ACTION '{}' to {}.".format(action, target))
            self.send_raw("PRIVMSG {} :\x01ACTION {}\x01".format(target, action))
        else:
            parser = formatter.IrcFormatter()
            self.logger.log("Sending parsed ACTION '{}' to {}.".format(action, target))
            self.send_raw("PRIVMSG {} :\x01ACTION {}\x01".format(target, parser.parse(action)))

    def ctcp(self, target, ctcp):
        self.logger.log("Sending CTCP '{}' to {}.".format(ctcp, target))
        self.send_raw("PRIVMSG {} :\x01{}\x01".format(target, ctcp))

    def ctcp_reply(self, target, ctcp, ctcpreply):
        self.logger.log("Sending CTCPREPLY '{}' to {}.".format(ctcp, target))
        self.send_raw("NOTICE {} :\x01{} {}\x01".format(target, ctcp, ctcpreply))

    def join_channel(self, channel):
        if len(self.disallowed_channels):
            for chan in self.disallowed_channels:
                if chan.lower() == channel:
                    self.logger.notice("Tried to join disallowed channel {}.".format(channel))
                    return False

        self.logger.log("Joining channel: {}".format(channel))
        self.send_raw("JOIN :{}".format(channel))

    def part_channel(self, channel, reason=None):
        if not reason:
            self.logger.log("Parting channel '{}'".format(channel))
            self.send_raw("PART {}".format(channel))
        else:
            self.logger.log("Parting channel '{}' with reason: {}".format(channel, reason))
            self.send_raw("PART {} :{}".format(channel, reason))

    def quit(self, message=None, callDisconnect=True):
        if not message:
            message = "{} shutting down.".format(self.currentnick)

        self.logger.log("Quitting IRC: {}".format(message))
        self.send_raw("QUIT :{}".format(message))

        if callDisconnect:
            self.disconnect()

    def disconnect(self, terminateThread=True):
        self.ratelimiter.stop()
        self.currentnick = None
        self.connected = False
        self.server_name = None
        self.socket.close()
        if terminateThread:
            self.running = False

    def nick(self, newnick):
        if not self.validator.nickname(newnick):
            self.logger.notice("Invalid nickname: {}".format(newnick))
            return False

        self.logger.log("Assuming new nickname '{}' (changing from {})".format(newnick, self.currentnick))
        self.send_raw("NICK :{}".format(newnick))
        self.currentnick = newnick
        return True

    def mode(self, target, modes):
        if not modes.startswith("+") and not modes.startswith("-") or len(modes) < 2:
            self.logger.notice("Trying to set invalid modes on {}: '{}'".format(target, modes))
            return False

        self.logger.log("Setting modes '{}' on {}".format(modes, target))
        self.send_raw("MODE {} {}".format(target, modes))
        return True

    def ban(self, nick, channel, quiet=False):
        mask = self.getMask(nick)
        if not mask:
            self.notice_verbose("Cannot get mask for {}/{}.".format(nick, channel))
            return False

        self.mode(channel, "+{} {}".format("q" if quiet else "b", mask))

        if not self.isOp(self.currentnick, channel):
            self.notice_verbose("Attempted to ban '{}' but was not an op in channel.".format(mask))
            return False
        return True

    def getMask(self, nick):
        ud = self.getUserData(nick.lower())
        bm = banmask.Banmask.createFromUserData(ud)

        if not bm:
            self.notice_verbose("Cannot create Mask {}: Banmask class was NoneType.".format(nick))
            return False

        mask = bm.getBestMatch()
        if mask:
            return mask
        return None

    def connect(self, reconnecting=False):
        if self.connected:
            raise Exception("Attempting to connect to {} when already connected as {}"
                            .format(self.server, self.currentnick))

        if self.ssl:
            self.logger.log("Attempting to connect to server ({}:{}) with SSL using {}."
                            .format(self.server, self.port, "IPv4" if self.ipv4 else "IPv6"))
            self._connect_ssl()
        else:
            self.logger.log("Attempting to connect to server. ({}:{}) using {}."
                            .format(self.server, self.port, "IPv4" if self.ipv4 else "IPv6"))
            self._connect()
        if not reconnecting:
            self.ratelimiter.start()
        else:
            self.ratelimiter = ratelimit.Ratelimit(self, self.logger)
            self.ratelimiter.start()

    def reconnect(self, message=None):
        if self.connected:
            if message:
                self.quit("Reconnecting: {}".format(message), False)
            else:
                self.quit("Reconnecting.", False)
            time.sleep(2)
        else:  # We quit by other means than user input.
            self.reconnect_attempts += 1
            time.sleep(2 * self.reconnect_attempts)

        self.disconnect(False)
        self.socket.close()

        self.connect(True)

    def identify(self):
        """Attempt to identify to services using the auth_string, returns True if auth_string was set, False if not."""
        if self._auth_string:
            self.send_raw(self._auth_string)
            self.logger.log_verbose("Identifying to services.")
            return True

        self.logger.log_verbose("Not identifying - no auth_string is set.")
        return False

    def send_who(self, nick):
        """
        Request /WHO data from server
        This data is prepended with '000' so the bot can distinguish it from other WHO requests.
        format: 000 user host nick status account realname
        This should be used to identify a single (or array of) users.
        """

        if self.last_uwho and nick == self.last_uwho:
            self.logger.log_verbose("send_who(): WHO {} prevented, recently WHO'd nick.".format(nick))
            return False

        if nick.startswith("#"):
            self.logger.error("send_who({}): expects a nick, not a channel.".format(nick))
            return False

        self.logger.log_verbose("send_who(): WHO {}".format(nick))
        self.send_raw("WHO {} %tuhnfar,000".format(nick))
        self.last_uwho = nick

    def send_chanwho(self, channel):
        """
        Request /WHO data from server
        This data is prepended with '001' so the bot can distinguish it from other WHO requests.
        format: 001 channel user host nick status account realname
        This should be used to identify a channel.
        """
        if not channel.startswith("#"):
            self.logger.error("send_chanwho({}) expects a channel, not a nick.".format(channel))
            return False
        if self.last_chanwho:
            if self.last_chanwho[0] == channel and int(time.time()) < self.last_chanwho[1] + 5:
                # Let's not flood the server too much, one chanwho per channel per 5 seconds
                self.logger.log_verbose("send_chanwho(): WHO {} prevented, recently WHO'd channel.".format(channel))
                return False

        if channel.lower() in self.channel_data:
            self.channel_data.pop(channel.lower())

        self.logger.log_verbose("send_chanwho(): WHO {}".format(channel))
        self.send_raw("WHO {} %tcuhnfar,001".format(channel))
        self.last_chanwho = [channel, int(time.time())]

    def isEvent(self, event):
        if event in ["PRIVMSG", "NOTICE", "MODE", "JOIN", "PART", "INVITE", "KICK", "QUIT"]:
            return True
        return False

    def processEvent(self, uinfo, event, target, params_list):
        nick = uinfo.split("!")[0]
        user = ""
        host = ""
        params = ""

        if event in ["PRIVMSG", "NOTICE", "JOIN", "PART", "KICK"] and self.validator.hostmask(uinfo):
            user = uinfo.split("@")[0][len(nick) + 1:]
            host = uinfo.split("@")[1]

            udata = self.getUserData(nick)  # Set host / ident so no /WHO is needed.
            if not udata:
                self.send_who(nick)

        if params_list:
            params = " ".join(params_list)
            if params.startswith(":"):
                params = params[1:]

        if target:
            if target.startswith(":"):
                target = target[1:]

        if event == "PRIVMSG":
            self.on_privmsg(nick, target, params, [nick, user, host, uinfo])
        elif event == "NOTICE":
            self.on_notice(nick, target, params)
        elif event == "MODE":
            self.on_mode(nick, target, params)
        elif event == "JOIN":
            self.on_join(nick, target)
        elif event == "PART":
            self.on_part(nick, target, params)
        elif event == "INVITE":
            self.on_invite(nick, params)
        elif event == "KICK":
            kreason = " ".join(params_list[1:])[1:]
            self.on_kick(nick, target, params_list[0], kreason if kreason else "No reason.")
        elif event == "QUIT":
            self.on_quit(nick, params)

    def on_privmsg(self, nick, target, message, uinfo=None):
        if message.startswith("\x01") and message.endswith("\x01"):
            if message.lstrip("\x01").startswith("ACTION"):
                self.on_action(nick, target, message.strip("\x01").strip("ACTION").strip())
            else:
                success = self.on_ctcp(nick, target, message.strip("\x01"))
                if success:
                    return True
        else:
            self.logger.event("PRIVMSG", "{}/{}: {}".format(nick, target, message))
            self.ModuleHandler.sendPrivmsg(target, nick, message)

        # Message looks like one of: nick: <cmd> | nick, <cmd> | nick <cmd>
        # or uses the command prefix.
        # or sent as query.
        if (target == self.currentnick or
           message.startswith(self.command_prefix) or
           (message.startswith(self.currentnick) and
               (message.startswith(self.currentnick + ":") or message.startswith(self.currentnick + ",") or
                message.startswith(self.currentnick + " ")))):
            self.on_command(nick, target, message, uinfo)

    def on_action(self, nick, target, message):
        self.logger.event("ACTION", "{}/{}: * {} {}".format(nick, target, nick, message))
        self.ModuleHandler.sendAction(target, nick, message)

    def on_ctcp(self, nick, target, ctcp):
        self.logger.event("CTCP", "{}/{}: {}".format(nick, target, ctcp))

        if ctcp == "CLIENTINFO":
            self.ctcp_reply(nick, ctcp, "CLIENTINFO MAINTAINER PING TIME VERSION")

        elif ctcp == "MAINTAINER":
            self.ctcp_reply(nick, ctcp, "Maintained by {}".format(self.config.getMaintainer()))

        elif ctcp == "TIME":
            self.ctcp_reply(nick, ctcp, "Current time: {}".format(time.strftime("%H:%M:%S - %A %d %B, %Y")))

        elif ctcp.startswith("PING"):
            self.ctcp_reply(nick, "PING", ctcp.strip("\x01")[5:])

        elif ctcp == "VERSION":
            self.ctcp_reply(nick, ctcp, "{} by {} v{} - {} - written in python".format(self.currentnick,
                            self.config.getMaintainer(), self.config.getVersion(), self.config.getGithubURL()))

        else:
            return False
        return True

    def on_notice(self, nick, target, message):
        if self.znc and self.znc_auth and nick == "irc.znc.in" and target == "AUTH":
            # Log in to ZNC.
            self.send_raw("PASS {}".format(self.znc_auth))
            self.znc = True
            self.znc_auth = False
        if target == "*":
            self.logger.log(message)
            self.server_name = nick  # TODO: This will be set four times, better ways? perhaps whois
        else:
            self.logger.event("NOTICE", "{}/{}: {}".format(nick, target, message))

    def on_mode(self, nick, target, modes):
        self.logger.event("MODE", "{}/{} sets mode: {}".format(nick, target, modes))
        if target.startswith("#") and ("o" in modes or "v" in modes):
            self.send_chanwho(target)

    def on_join(self, nick, channel):
        self.logger.event("JOIN", "{} joined {}".format(nick, channel))

        if nick != self.currentnick:
            if channel.lower() in self.channel_data:
                self.channel_data[channel.lower()]["regular"].append(nick.lower())
            else:
                self.logger.notice_verbose("on_join({}, {}): channel was not in channel_data".format(nick, channel))
                self.send_chanwho(channel)
        else:
            self.send_chanwho(channel)
            if channel not in self.channels:
                self.channels.append(channel)
                self.channelmanager.add(channel)

        self.ModuleHandler.sendJoin(nick, channel)

    def on_part(self, nick, channel, message=None):
        if not message:
            self.logger.event("PART", "{} parted {}".format(nick, channel))
        else:
            self.logger.event("PART", "{} parted {}: {}".format(nick, channel, message))

        if nick != self.currentnick:
            self.channeldata_remove_user(nick, channel)

            self.check_channel_empty(channel)
        else:
            self.channelmanager.delete(channel)
            if channel.lower() in self.channel_data:
                self.channel_data.pop(channel.lower())

            if channel in self.channels:
                self.channels.remove(channel)

        self.ModuleHandler.sendPart(nick, channel, message)

    def on_kick(self, nick, channel, knick, reason):
        self.logger.event("KICK", "{} was kicked from {} by {}: {}".format(knick, channel, nick, reason))

        if knick == self.currentnick:
            self.channelmanager.delete(channel)
            if channel.lower() in self.channel_data:
                self.channel_data.pop(channel.lower())
            if channel in self.channels:
                self.channels.remove(channel)
        else:
            self.check_channel_empty(channel)

        self.ModuleHandler.sendKick(nick, channel, knick, reason)

    def on_invite(self, nick, channel):
        self.logger.event("INVITE", "{} invited me to join {}".format(nick, channel))

        if self.invite_join:
            self.join_channel(channel)

    def on_quit(self, nick, message=None):
        self.logger.event("QUIT", "{} has quit IRC: {}".format(nick, "Quit" if not message else message))

        for chan in self.channel_data:
            if self.isOn(nick, chan):
                self.channeldata_remove_user(nick, chan)
                self.check_channel_empty(chan)

        if nick == self.currentnick and self.connected:
            self.logger.notice("We have disconnected from {}, attempting to reconnect.".format(self.server_name))
            self.reconnect()

        self.ModuleHandler.sendQuit(nick, message)

    def on_command(self, nick, target, message, uinfo):
        split = message.split()
        command = ""
        params = ""
        ttarget = target

        if message.startswith(self.command_prefix):
            command = split[0][1:]
            params = " ".join(split[1:])
        elif message.startswith(self.currentnick):
            if len(split) == 1:
                return False  # command too short.

            command = split[1]
            params = " ".join(split[2:])
        elif target == self.currentnick:  # Query
            command = split[0]
            params = " ".join(split[1:])
            ttarget = nick
        else:
            # This cannot be a valid command.
            return False

        admin = self.config.isAdministrator(self.network_name, uinfo[3])
        mod = self.config.isModerator(self.network_name, uinfo[3])
        command = command.lower()

        success = self.ModuleHandler.sendCommand(ttarget, nick, command, params, mod, admin)

        self.logger.event("COMMAND", "{}/{} sent command '{}' with result: {}"
                                     .format(nick, target, command, "Success" if success else "Command did not exist"))

        if (not success and target == self.currentnick and nick != self.currentnick and
            ((nick not in self.cmdhelp_delays) or  # Not in cmdhelp dict or 10 seconds passed.
             (nick in self.cmdhelp_delays and int(time.time()) > self.cmdhelp_delays[nick] + 10))):
            self.say(nick, ("I'm sorry, but I did not understand the command '$(bold){}$(bold)'. " +
                            "Try $(bold){}help$(bold) for more information about my commands.")
                     .format(command, self.command_prefix), True)
            self.cmdhelp_delays[nick] = int(time.time())

        return success

    def on_numeric(self, numeric, data):
        """
        The ircd sends numerics to indicate something is wrong (or right),
        This method will interact with a few of them

        https://www.alien.net.au/irc/irc2numerics.html
        """

        if numeric == 354:
            # RPL_WHOREPLY
            whodata = data.split()[3:]
            if len(whodata):
                self.on_whoreply(whodata)

        if numeric == 433:
            # Nick is already taken.
            if self.currentnick != self.altnick:
                self.nick(self.altnick)

        if numeric == 422 or numeric == 376:
            # No MOTD found or End of MOTD

            # Set name to what it really is as provided by the server over what we think it is.
            nick = data.split()[2]
            if nick != self.currentnick:
                self.logger.notice_verbose("Incorrect currentnick: {} -> {}".format(self.currentnick, nick))
                self.currentnick = nick

            self.identify()  # Identify to services.

            if self.modes:
                self.mode(self.currentnick, self.modes)

            if len(self.channels):
                self.send_raw("JOIN :" + ",".join(self.channels))
            else:
                self.logger.log_verbose("Not configured to join any channels.")

            if self.perform:
                for perform in self.perform:
                    self.send_raw(perform)

            if not self.server_name:
                self.logger.notice_verbose("Could not retrieve server name, using network name instead.")
                self.server_name = self.network_name

            self.logger.log("A connection has been established with {}.".format(self.server_name))

        self.ModuleHandler.sendNumeric(numeric, data)
        return False

    def on_whoreply(self, args):
        """Handles custom WHO requests by the bot."""

        if args[0] == "000" and len(args) >= 7:  # self.send_who() response
            """format: 000 user host nick status account realname"""

            iName = args[3].lower()
            if iName in self.user_data:  # Refresh data with newer data.
                self.user_data.pop(iName)

            self.user_data[iName] = {
                "identified":  True if args[5] != "0" else False,
                "account": args[5],  # Will contain 0 if not identified.
                "nick": args[3],
                "user": args[1],
                "host": args[2],
                "away": "G" in args[4],
                "oper": "*" in args[4],
                "realname": " ".join(args[6:])[1:]
            }
        elif args[0] == "001" and len(args) >= 8:  # self.send_chanwho() response
            """format: 001 channel user host nick status account realname"""

            iName = args[4].lower()
            if iName in self.user_data:  # Refresh data with newer data.
                self.user_data.pop(iName)

            self.user_data[iName] = {
                "identified":  True if args[6] != "0" else False,
                "account": args[6],  # Will contain 0 if not identified.
                "nick": args[4],
                "user": args[2],
                "host": args[3],
                "away": "G" in args[5],
                "oper": "*" in args[5],
                "realname": " ".join(args[7:])[1:]
            }

            iChan = args[1].lower()
            iNick = args[4].lower()
            if iChan not in self.channel_data:
                self.channel_data[iChan] = {"op": [], "voice": [], "regular": []}

            if "@" in args[5]:
                self.channel_data[iChan]["op"].append(iNick)
            elif "+" in args[5]:
                self.channel_data[iChan]["voice"].append(iNick)
            else:
                self.channel_data[iChan]["regular"].append(iNick)

    def channeldata_remove_user(self, nick, channel):
        """Check if user is in channel data array, remove if they are"""
        nick = nick.lower()
        channel = channel.lower()

        if channel in self.channel_data:
            if self.isOp(nick, channel):
                self.channel_data[channel]["op"].remove(nick)
            elif self.isVoice(nick, channel):
                self.channel_data[channel]["voice"].remove(nick)
            elif self.isOn(nick, channel):
                self.channel_data[channel]["regular"].remove(nick)

    def isOp(self, nick, channel):
        nick = nick.lower()
        channel = channel.lower()

        if channel in self.channel_data:
            return nick in self.channel_data[channel]["op"]
        return False

    def isVoice(self, nick, channel):
        nick = nick.lower()
        channel = channel.lower()

        if channel in self.channel_data:
            return nick in self.channel_data[channel]["op"] or nick in self.channel_data[channel]["voice"]
        return False

    def isOn(self, nick, channel):
        nick = nick.lower()
        channel = channel.lower()

        if channel in self.channel_data:
            return (nick in self.channel_data[channel]["op"] or
                    nick in self.channel_data[channel]["voice"] or
                    nick in self.channel_data[channel]["regular"])
        return False

    def isOper(self, nick):
        nick = nick.lower()

        if nick in self.user_data:
            return self.user_data[nick]["oper"]
        return False

    def isIdentified(self, nick):
        nick = nick.lower()

        if nick in self.user_data:
            return self.user_data[nick]["identified"]
        return False

    def isBotAdmin(self, nick):
        nick = nick.lower()

        if nick in self.user_data:
            usermask = "{}!{}@{}".format(self.user_data[nick]["nick"],
                                         self.user_data[nick]["user"],
                                         self.user_data[nick]["host"])
            return self.config.isAdministrator(self.network_name, usermask)
        return False

    def isBotModerator(self, nick):
        nick = nick.lower()

        if nick in self.user_data:
            usermask = "{}!{}@{}".format(self.user_data[nick]["nick"],
                                         self.user_data[nick]["user"],
                                         self.user_data[nick]["host"])
            return self.config.isModerator(self.network_name, usermask)
        return False

    def getUserData(self, nick):
        nick = nick.lower()

        if nick in self.user_data:
            return self.user_data[nick]
        return False

    def getChannelData(self, channel):
        channel = channel.lower()

        if channel in self.channel_data:
            return self.channel_data[channel]
        return False

    def isRunning(self):
        return True if self.running else False

    def getName(self):
        return self.server_name if "server_name" in self else self.network_name

    def check_channel_empty(self, channel):
        if self.leave_empty_channels:
            ucount = 0
            cdata = self.getChannelData(channel)
            if cdata:
                for value in cdata.items():
                    for user in value[1]:
                        ucount += 1

            if ucount == 1:
                self.part_channel(channel, "Channel is empty, leaving channel.")

    def register_command(self, command, params, help, priv, aliases=None, module=None):
        self.commandhelp.register(command, params, help, priv, aliases, module)

    def unregister_command(self, command):
        self.commandhelp.unregister(command)

    def loadNetworkVariables(self, network=None, curnick=None):
        """variables that will get created on initialisation, recreated on rehash"""
        if not network:
            network = self.network

        self.id = network["id"]
        self.network_name = network["network_name"]
        self.server_name = None  # Gets set upon connecting.
        self.server = network["server"]
        self.port = network["port"]
        self.ssl = network["ssl"]
        self.ipv4 = network["ipv4"]

        self.znc = type(network["znc"]) == str  # False if not using znc, true otherwise.
        if self.znc:
            # the user/network:password phrase if self.znc is true
            # for security reasons, this will unset itself automatically once used.
            self.znc_auth = network["znc"]
        else:
            self.znc_auth = False

        self.mnick = network["nick"]
        self.altnick = network["altnick"]
        self.user = network["user"]
        self.realname = network["realname"]

        self._auth_string = network["auth_string"]

        self.command_prefix = network["command_prefix"]
        self.invite_join = network["invite_join"]
        self.leave_empty_channels = network["leave_empty_channels"]
        self.modes = network["modes"]
        self.perform = network["perform"]

        self.channels = network["channels"]
        self.debug_chan = network["debug_chan"]

        self.administrators = network["administrators"]
        self.moderators = network["moderators"]

        self.disallowed_channels = network["disallowed_channels"]

        self.currentnick = curnick

        self.queue_privmsg = queue.Queue()
        self.queue_notice = queue.Queue()

        self.user_data = {}  # Data gathered by /WHO
        self.last_uwho = None
        self.channel_data = {}
        self.last_chanwho = None  # Last channel who (self.send_chanwho())
        self.cmdhelp_delays = {}  # Pause before telling someone their command was not correct to avoid endless loops

        self.reconnect_attempts = 0  # Each time we reconnect we take a bit longer to reconnect.

        self.logger = logger.Logger(self.network_name, self.config.getLogging(), self.config.getVerbose(),
                                    self.config.getTimestampFormat(), self.config.getLogTimestampFormat(),
                                    self.config.getMetadata("logger_terminal_colours"))
        self.validator = validator.Validator()
        self.channelmanager = channel.ChannelManager(self.config.getDatabaseDir(), self.logger, self.network_name,
                                                     self.validator)
        self.commandhelp = commandhelp.CommandHelp(self.logger, self.config.getCommandPrefix(self.network_name))
        self.ratelimiter = ratelimit.Ratelimit(self, self.logger)

        self.errors_per_minute = 0  # If we get too many EPM (errors per minute), we stop.
        self.time_error_per_minute = int(time.time())

    def _connect_ssl(self):
        sock = None

        try:
            if self.ipv4:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.server, self.port))
            else:
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.connect((self.server, self.port, 0, 0))
        except Exception:
            self.reconnect()
            return

        self.socket = ssl.wrap_socket(sock)

        self.send_raw("NICK {}".format(self.mnick))
        self.currentnick = self.mnick
        # <username> <hostname> <servername> :<realname> - servername/hostname will be ignored by the ircd.
        self.send_raw("USER {} 0 0 :{}".format(self.user, self.realname))
        self.connected = True

    def _connect(self):
        try:
            if self.ipv4:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.server, self.port))
            else:
                self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                self.socket.connect((self.server, self.port, 0, 0))
        except Exception:
            self.reconnect()
            return

        self.send_raw("NICK {}".format(self.mnick))
        self.currentnick = self.mnick
        # <username> <hostname> <servername> :<realname> - servername/hostname will be ignored by the ircd.
        self.send_raw("USER {} 0 0 :{}".format(self.user, self.realname))
        self.connected = True

    def _loadModules(self):
        self.ModuleHandler = module.ModuleHandler(self)
        self.ModuleHandler.loadAll()

    def _getPrivmsgQueue(self):
        """Gets the message queue from the ratelimiter thread."""
        return self.queue_privmsg

    def _getNoticeQueue(self):
        return self.queue_notice
