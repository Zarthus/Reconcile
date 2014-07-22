"""
IRC class for irc connections
"""

import socket
import time
import re

from ssl import wrap_socket
from ssl import CERT_NONE
from ssl import CERT_REQUIRED
from ssl import SSLError

from core import channel
from core import module
from core import commandhandler
from tools import validator
from tools import formatter


class IrcConnection:
    def __init__(self, network, config, modules=None):
        self.config = config
        self.loadNetworkVariables(network)
        self._loadModules()

        self.numeric_regex = re.compile(":.* [0-9]{3}")

        self.connect()

    def tick(self):
        self.readBuffer()

    def readBuffer(self):
        buff = self.socket.recv(4096)
        lines = buff.decode("utf-8").split("\n")
        for data in lines:
            data = str(data).strip()

            if not data:
                continue
            print(">> {} | {}".format(self.server, data))

            words = data.split()

            if len(words) > 1:
                if words[0] == "PING":
                    # Reply to PING
                    self.send_raw("PONG " + words[1])
                    continue

                if self.numeric_regex.match(" ".join(words[:2])):
                    # Check if a server numeric is sent, and handle it appropriately.
                    if self._processIrcNumeric(words[1], data):
                        # _processIrcNumeric returns true if we need to continue, false if we don't
                        continue

                if self.isEvent(words[1]):
                    # Most(?) events share the following syntax:
                    # :nick!user@host EVENT target [[:]message/params]

                    uinfo = words[0][1:]
                    event = words[1]
                    target = words[2]
                    params = words[3:] if len(words) > 3 else None

                    self._processEvent(uinfo, event, target, params)

    def send_raw(self, data):
        print("<< {} | {}".format(self.server, data))
        self.socket.send(bytes(data + "\r\n", "utf-8"))

    def say(self, target, message, format=False):
        """
        Sends a message to target
        With formatting enabled, we will attempt to parse the contents through the IrcFormatter class.
        """

        if not format:
            self.send_raw("PRIVMSG {} :{}".format(target, message))
        else:
            parser = formatter.IrcFormatter()
            self.send_raw("PRIVMSG {} :{}".format(target, parser.parse(message)))

    def action(self, target, action, format=False):
        """
        Sends a CTCP ACTION to target
        With formatting enabled, we will attempt to parse the contents through the IrcFormatter class.
        """

        if not format:
            self.send_raw("PRIVMSG {} :\x01ACTION {}\x01".format(target, message))
        else:
            parser = formatter.IrcFormatter()
            self.send_raw("PRIVMSG {} :\x01ACTION {}\x01".format(target, parser.parse(message)))

    def notice(self, target, notice, format=False):
        """
        Sends a NOTICE to target
        With formatting enabled, we will attempt to parse the contents through the IrcFormatter class.
        """

        if not format:
            self.send_raw("NOTICE {} :{}".format(target, notice))
        else:
            parser = formatter.IrcFormatter()
            self.send_raw("NOTICE {} :{}".format(target, parser.parse(notice)))

    def ctcp(self, target, ctcp):
        self.send_raw("PRIVMSG {} :\x01{}\x01".format(target, ctcp))

    def ctcp_reply(self, target, ctcp, ctcpreply):
        self.send_raw("NOTICE {} :\x01{} {}\x01".format(target, ctcp, ctcpreply))

    def join(self, channel):
        self.send_raw("JOIN :{}".format(channel))

    def part(self, channel):
        self.send_raw("PART :{}".format(channel))

    def quit(self, message=None):
        if not message:
            message = "{} shutting down.".format(self.currentnick)

        self.send_raw("QUIT :{}".format(message))
        self.currentnick = None
        self.connected = False

    def nick(self, newnick):
        if self.validator.nickname(newnick):
            print("Invalid nickname: {}".format(newnick))
            return False

        self.send_raw("NICK :{}".format(newnick))
        self.currentnick = newnick
        return True

    def connect(self):
        if self.connected:
            raise Exception("Attempting to connect to {} when already connected as {}"
                            .format(self.server, self.currentnick))

        if self.ssl:
            self._connect_ssl()
        else:
            self._connect()

    def reconnect(self, message=None):
        if not self.connected:
            raise Exception("Cannot reconnect to {} - no connection has been established".format(self.server))

        if message:
            self.quit("Reconnecting: {}".format(message))
        else:
            self.quit("Reconnecting.")

        # TODO: Sleep Thread (1s) once implemented
        self.connect()

    def isEvent(self, event):
        if event in ["PRIVMSG", "NOTICE", "MODE", "JOIN", "PART", "INVITE", "KICK", "QUIT"]:
            return True
        return False

    def on_privmsg(self, nick, target, message, uinfo=None):
        if message.startswith("\x01") and message.endswith("\x01"):
            if message.lstrip("\x01").startswith("ACTION"):
                self.on_action(nick, target, message.strip("\x01").strip("ACTION"))
            else:
                self.on_ctcp(nick, target, message.strip("\x01"))

        if message.startswith(self.command_prefix) or message.startswith(self.currentnick):
            self.on_command(nick, target, message, uinfo)

        self.ModuleHandler.sendPrivmsg(target, nick, message)

    def on_action(self, nick, target, message):
        self.ModuleHandler.sendAction(target, nick, message)

    def on_ctcp(self, nick, target, ctcp):
        if ctcp == "VERSION":
            self.ctcp_reply(nick, ctcp, "{} by {} v{} - {} - written in python".format(self.currentnick,
                            self.config.getMaintainer(), self.config.getVersion(), self.config.getGithubURL()))

        elif ctcp == "MAINTAINER":
            self.ctcp_reply(nick, ctcp, "Maintained by {}".format(self.config.getMaintainer()))

        elif ctcp == "TIME":
            self.ctcp_reply(nick, ctcp, "Current time: {}".format(time.strftime("%H:%M:%S - %A %d %B, %Y")))

        elif ctcp == "PING":
            self.ctcp_reply(nick, ctcp, "PONG - {}".format(time.ctime()))

    def on_notice(self, nick, target, message):
        pass

    def on_mode(self, nick, target, modes):
        pass

    def on_join(self, nick, channel):
        if nick == self.currentnick:
            self.channelmanager.addForNetwork(self.network_name, channel)
            if channel not in self.channels:
                self.channels.append(channel)

    def on_part(self, nick, channel):
        if nick == self.currentnick:
            self.channelmanager.delForNetwork(self.network_name, channel)
            if channel in self.channels:
                self.channels.remove(channel)

    def on_kick(self, nick, channel, knick, reason):
        if knick == self.currentnick:
            self.channelmanager.delForNetwork(self.network_name, channel)
            if channel in self.channels:
                self.channels.remove(channel)

    def on_invite(self, nick, channel):
        if self.invite_join:
            self.join(channel)

    def on_quit(self, nick, message=None):
        pass

    def on_command(self, nick, target, message, uinfo):
        split = message.split()
        command = ""
        params = ""

        if message.startswith(self.command_prefix):
            command = split[0][1:]
            params = split[1:]
        elif message.startswith(self.currentnick):
            command = split[1]
            params = split[2:]
        else:
            # This cannot be a valid command.
            return False

        info = {
            "nick": nick,
            "target": target,

            "admin": self.config.isAdministrator(self.network_name, uinfo[3]),
            "mod": self.config.isModerator(self.network_name, uinfo[3]),

            "IrcConnection": self,
            "command_prefix": self.command_prefix
        }

        cmd = commandhandler.CommandHandler(command.lower(), params, info)
        mod = self.ModuleHandler.sendCommand(target, nick, command, params, info["mod"], info["admin"])

        return cmd.getSuccess() or mod

    def loadNetworkVariables(self, network):
        self.connected = False

        self.id = network["id"]
        self.network_name = network["network_name"]
        self.server = network["server"]
        self.port = network["port"]
        self.ssl = network["ssl"]

        self.nick = network["nick"]
        self.altnick = network["altnick"]
        self.ident = network["ident"]
        self.realname = network["realname"]

        self.account = network["account"]
        self.password = network["password"]

        self.command_prefix = network["command_prefix"]
        self.invite_join = network["invite_join"]

        self.channels = network["channels"]

        self.administrators = network["administrators"]
        self.moderators = network["moderators"]

        self.currentnick = None

        self.validator = validator.Validator()
        self.channelmanager = channel.ChannelManager(self.config.getDatabaseDir(), self.validator)

    def _connect_ssl(self):
        raise NotImplementedError("Connecting to SSL has not yet been implemented.")

    def _connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server, self.port))
        self.send_raw("NICK {}".format(self.nick))
        self.currentnick = self.nick
        # <username> <hostname> <servername> :<realname> - servername/hostname will be ignored by the ircd.
        self.send_raw("USER {} 0 0 :{}".format(self.ident, self.realname))
        self.connected = True

    def _processIrcNumeric(self, numeric, data):
        """
        The ircd sends numerics to indicate something is wrong (or right),
        This method will interact with a few of them
        """

        if numeric == "433":
            # Nick is already taken.
            self.send_raw("NICK " + self.altnick)
            self.currentnick = self.altnick
            return True

        if numeric == "422" or numeric == "376":
            # No MOTD found or End of MOTD
            if self.password and self.account:
                self.send_raw("PRIVMSG NickServ :IDENTIFY {} {}".format(self.account, self.password))

            self.send_raw("JOIN :" + ",".join(self.channels))

        return False

    def _processEvent(self, uinfo, event, target, params_list):
        nick = uinfo.split("!")[0]
        user = ""
        host = ""
        params = ""

        if event in ["PRIVMSG", "NOTICE", "JOIN", "PART", "KICK"] and self.validator.hostmask(uinfo):
            user = uinfo.split("@")[0][len(nick) + 1:]
            host = uinfo.split("@")[1]

        if params_list and " ".join(params_list).startswith(":"):
            params = " ".join(params_list)[1:]

        if event == "PRIVMSG":
            self.on_privmsg(nick, target, params, [nick, user, host, uinfo])
        elif event == "NOTICE":
            self.on_notice(nick, target, params)
        elif event == "MODE":
            self.on_mode(nick, target, params)
        elif event == "JOIN":
            self.on_join(nick, target)
        elif event == "PART":
            self.on_part(nick, target)
        elif event == "INVITE":
            self.on_invite(nick, params)
        elif event == "KICK":
            self.on_kick(nick, channel, target, params)
        elif event == "QUIT":
            self.on_quit(nick, params)

        # TODO: handle modules ..

    def _loadModules(self):
        self.ModuleHandler = module.ModuleHandler(self)
        self.ModuleHandler.loadAll()
