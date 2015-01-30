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

banmask.py:

Return best matching bans based on the information available.

Note: Whenever a banmask is not available, the value returned will be None.
ENSURE you have `if banmask:` prior to setting the banmask.
"""

BANMASK_BEST = 0
BANMASK_DEFAULT = 1
BANMASK_IDENTD = 1
BANMASK_USER = 1  # Alias of BANMASK_IDENTD
BANMASK_ACCOUNT = 2
BANMASK_HOST = 3
BANMASK_NICK = 4


class Banmask:

    def __init__(self, nick, ident=None, host=None, account=None):
        self.nick = nick
        self.ident = ident
        self.host = host
        self.account = account

    def createFromUserData(user_data):
        """Create a banmask class from a 'self.getUserData(nick)'"""
        if not user_data:
            return None

        (nick, ident, host, account) = (None, None, None, None)

        if "nick" in user_data and user_data["nick"]:
            nick = user_data["nick"]
        if "user" in user_data and user_data["user"]:
            ident = user_data["user"]
        if "host" in user_data and user_data["host"]:
            host = user_data["host"]
        if ("account" in user_data and user_data["account"] and
                user_data["account"] != "0"):
            account = user_data["account"]

        return Banmask(nick, ident, host, account)

    def get(self, BANMASK_TYPE=BANMASK_DEFAULT):
        banmasks = {
            BANMASK_BEST: self.getBestMatch(),
            BANMASK_IDENTD: self.getIdentdMask(),
            BANMASK_ACCOUNT: self.getAccountMask(),
            BANMASK_HOST: self.getHostMask(),
            BANMASK_NICK: self.getNickMask()
        }

        if BANMASK_TYPE in banmasks:
            return banmasks[BANMASK_TYPE]
        return None

    def getBestMatch(self):
        if self.getAccountMask():
            return self.getAccountMask()

        if self.getIdentdMask():
            return self.getIdentdMask()

        if self.getHostMask():
            return self.getHostMask()

        if self.getNickMask():
            return self.getNickMask()
        return None

    def getNickMask(self):
        if self.nick:
            return "{}!*@*".format(self.nick)
        return None

    def getIdentdMask(self):
        if self.ident and self.host:
            if self.ident.startswith("~"):
                return "*!*@{}".format(self.host)
            else:
                return "*!{}@{}".format(self.ident, self.host)
        return None

    def getHostMask(self):
        if self.host:
            return "*!*@{}".format(self.host)
        return None

    def getAccountMask(self):
        if self.account:
            return "$a:{}".format(self.account)
        return None

    def getFullMask(self):
        if self.nick and self.ident and self.host:
            return "{}!{}@{}".format(self.nick, self.ident, self.host)
        return None
