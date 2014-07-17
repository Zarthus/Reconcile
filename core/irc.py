"""
IRC class for irc connections
"""

import socket
import thread
import re

from ssl import wrap_socket
from ssl import CERT_NONE
from ssl import CERT_REQUIRED
from ssl import SSLError

from core import channel
from tools import validator


class IrcConnection:
    def __init__(self, network, config, modules=None):
        self.config = config
        self.loadNetworkVariables(network)

        self.connect()

    def tick(self):
        self.readBuffer()

    def readBuffer(self):
        buffer = self.socket.recv(4096)
        lines = buffer.split("\n")
        for data in lines:
            data = str(data).strip()

            if not data:
                continue
            print(">> {} | {}".format(self.server, data))

            words = data.split()

            # TODO: write function to check if numeric.
            if len(words) > 1:

                if words[0] == "PING":
                    # Reply to PING
                    self.send_raw("PONG " + words[1])
                    continue

                if words[1] == "443":
                    # Nick is already taken.
                    self.send_raw("NICK " + self.altnick)
                    self.currentnick = self.altnick
                    continue

                if words[1] == "422" or words[1] == "376":
                    # No MOTD found or End of MOTD
                    self.send_raw("JOIN :" + ",".join(self.channels))

    def send_raw(self, data):
        self.socket.send(data + "\r\n")
        print("<< {} | {}".format(self.server, data))

    def say(self, target, message):
        self.send_raw("PRIVMSG {} :{}".format(target, message))

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

    def checkRequests(self):
        pass

    def loadNetworkVariables(self, network):
        self.connected = False

        self.id = network["id"]
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
        self.socket = socket.socket()
        self.socket.connect((self.server, self.port))
        self.send_raw("NICK {}".format(self.nick))
        self.currentnick = self.nick
        # <username> <hostname> <servername> :<realname> - servername/hostname will be ignored by the ircd.
        self.send_raw("USER {} 0 0 :{}".format(self.ident, self.realname))
        self.connected = True
