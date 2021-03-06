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

WhoDebug by Zarthus
Licensed under MIT

This module will allow you to debug send_chanwho() and send_who() data.
"""

from core import moduletemplate
from tools import paste
import pprint


class WhoDebug(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("userdata", "<nick>", "Gist all data we have regarding WHO on nick.", self.PRIV_ADMIN)
        self.register_command("channeldata", "<channel>", "Gist all data we have regarding WHO on channels.",
                              self.PRIV_ADMIN)
        self.register_command("isadmin", "<nick>", "Is <nick> a bot administrator?", self.PRIV_ADMIN)
        self.register_command("ismod", "<nick>", "Is <nick> a bot moderator?", self.PRIV_ADMIN)
        self.register_command("isop", "<nick> <chan>", "Is <nick> an op on <chan>", self.PRIV_ADMIN)
        self.register_command("isvoice", "<nick> <chan>", "Is <nick> a voice on <chan>", self.PRIV_ADMIN)
        self.register_command("ison", "<nick> <chan>", "Is <nick> on <chan>", self.PRIV_ADMIN)
        self.register_command("isidentified", "<nick>", "Is <nick> identified to his account?", self.PRIV_ADMIN)
        self.register_command("isoper", "<nick>", "Is <nick> an operator of the network?", self.PRIV_ADMIN)

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if admin:
            if command == "channeldata":
                if not commandtext:
                    return self.notice(nick, "Usage: channeldata <channel>")

                data = pprint.pformat(self.getChannelData(commandtext))

                return self.notice(nick, paste.Paste.gist("Channel Data of {}".format(commandtext),
                                                          data, logger=self.logger))

            if command == "userdata":
                if not commandtext:
                    return self.notice(nick, "Usage: userdata <channel>")

                data = pprint.pformat(self.getUserData(commandtext))

                return self.notice(nick, paste.Paste.gist("User Data of {}".format(commandtext),
                                                          data, logger=self.logger))

            if command == "isidentified":
                if not commandtext:
                    return self.notice(nick, "Usage: isidentified <nick>")

                return self.message(target, nick, self.isIdentified(commandtext))

            if command == "isoper":
                if not commandtext:
                    return self.notice(nick, "Usage: isoper <nick>")

                return self.message(target, nick, self.isOper(commandtext))

            if command == "isadmin":
                if not commandtext:
                    return self.notice(nick, "Usage: isadmin <nick>")

                return self.message(target, nick, self.isBotAdmin(commandtext))

            if command == "ismod":
                if not commandtext:
                    return self.notice(nick, "Usage: ismod <nick>")

                return self.message(target, nick, self.isBotMod(commandtext))

            if command == "isop":
                cmdtxt = commandtext.split()

                if not commandtext or len(cmdtxt) != 2:
                    return self.notice(nick, "Usage: isop <nick> <channel>")

                return self.message(target, nick, self.isOp(cmdtxt[0], cmdtxt[1]))

            if command == "isvoice":
                cmdtxt = commandtext.split()

                if not commandtext or len(cmdtxt) != 2:
                    return self.notice(nick, "Usage: isvoice <nick> <channel>")

                return self.message(target, nick, self.isVoice(cmdtxt[0], cmdtxt[1]))

            if command == "ison":
                cmdtxt = commandtext.split()

                if not commandtext or len(cmdtxt) != 2:
                    return self.notice(nick, "Usage: ison <nick> <channel>")

                return self.message(target, nick, self.isOn(cmdtxt[0], cmdtxt[1]))

        return False
