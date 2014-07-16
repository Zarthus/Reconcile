"""
IRC class for irc connections
"""

import socket
import thread

from ssl import wrap_socket
from ssl import CERT_NONE
from ssl import CERT_REQUIRED
from ssl import SSLError


class IrcConnection:
    def __init__(self, network, modules=None):
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

            words = data.split()

            if words[0] == "PING":
                # Reply to PING
                self.send_raw("PONG " + words[1])
                continue

            if words[1] == "443":
                # Nick is already taken.
                self.send_raw("NICK " + self.altnick)
                continue

            if words[1] == "422" or words[1] == "376":
                # No MOTD found or End of MOTD
                self.send_raw("JOIN :" + self.channels)

            print(">> " + data)

    def send_raw(self, data):
        self.socket.send(data + "\r\n")
        print("<< " + data)

    def say(self, target, message):
        self.send_raw("PRIVMSG {} :{}".format(target, message))

    def connect(self):
        if self.ssl:
            self._connect_ssl()
        else:
            self._connect()

    def checkRequests(self):
        pass

    def loadNetworkVariables(self, network):
        self.id = int(network["id"])
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

        self.administrators = network["administrators"]
        self.moderators = network["moderators"]

        self.channels = "#zarthus"

    def _connect_ssl(self):
        pass

    def _connect(self):
        self.socket = socket.socket()
        self.socket.connect((self.server, self.port))
        self.send_raw("NICK {}".format(self.nick))
        # <username> <hostname> <servername> :<realname> - servername/hostname will be ignored by the ircd.
        self.send_raw("USER {} 0 0 :{}".format(self.ident, self.realname))
