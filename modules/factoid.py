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

factoid.py by Zarthus
Licensed under MIT

Factoids: brief answers to frequently asked questions and other responses.
"""

from core import moduletemplate
from tools import formatter
from tools import validator

import os
import sqlite3
import time


class Factoid(moduletemplate.BotModule):

    def on_module_load(self):
        self.colformat = formatter.IrcFormatter()
        self.validator = validator.Validator()

        self.db_file = os.path.join(self.db_dir, "{}_factoids.db".format(self.network_name))
        self.factoid_make_db()

        if "global_factoids" not in self.module_data:
            self.module_data["global_factoids"] = False

        globparam = " [-global]" if not self.module_data["global_factoids"] else ""
        globstr = ""

        if not self.module_data["global_factoids"]:
            globstr = " Use [-global] for global factoids."

        self.register_command("isfactoid", "<factoid>", "Check if <factoid> exists and return information if it does.",
                              self.PRIV_NONE, ["factoid"])
        self.register_command("addfactoid", "<factoid> <response>" + globparam,
                              "Adds <factoid> with <response> to the factoid database." + globstr, self.PRIV_MOD)
        self.register_command("editfactoid", "<factoid> <new response>" + globparam,
                              "Edits <factoid> with <new response>." + globstr, self.PRIV_MOD)
        self.register_command("delfactoid", "<factoid>" + globparam,
                              "Deletes <factoid> from the factoid database." + globstr, self.PRIV_MOD)
        self.register_command("countfactoid", globparam.lstrip() if globparam else None,
                              "Returns the number of factoids in the database." + globstr,
                              self.PRIV_MOD, ["countfactoids"])

    def on_privmsg(self, target, nick, message):

        if self.factoid_isrequest(message):
            if message.startswith("$$"):
                words = message.split()
                factoid = words[1]

                channel = self.factoid_getchannel(target, message)

                if not self.factoid_isvalid(factoid):
                    self.notice(nick, "Factoid request '{}' is an invalid factoid trigger name.".format(factoid))
                elif self.factoid_exists(factoid):
                    self.message(target, None, self.factoid_getresponse(factoid, channel), True)
                else:
                    self.notice(nick, "Could not find factoid '{}' in my database.".format(factoid))
            else:
                channel = self.factoid_getchannel(target, message)
                message = message.replace(" -global", "").strip()
                words = message.split()

                if len(words) < 3:
                    return self.notice(nick, "Syntax error, usage: $? <nick> <factoid>")
                ftarget = words[1]
                factoid = words[2]

                if not self.factoid_isvalid(factoid):
                    self.notice(nick, "Factoid request '{}' is an invalid factoid trigger name.".format(factoid))
                elif self.factoid_exists(factoid):
                    self.message(target, None, "{}: {}".format(ftarget, self.factoid_getresponse(factoid, channel)),
                                 True)
                else:
                    self.notice(nick, "Could not find factoid '{}' in my database.".format(factoid))

            return True
        else:
            words = message.split()
            for word in words:
                if self.factoid_isaltrequest(word):
                    # Slice off [[ ]]
                    factoid = word[2:-2]
                    ftarget = None

                    # check if it was targeting a name [[name:factoid]]
                    if ":" in factoid:
                        split = factoid.split(":")
                        ftarget = split[0]

                        if len(split) > 1:
                            factoid = split[1]

                        if not self.validator.nickname(ftarget):
                            ftarget = None
                            factoid = split[0]

                    if self.factoid_exists(factoid):
                        self.message(target, ftarget, self.colformat.parse(self.factoid_getresponse(factoid)))
                    else:
                        self.notice(nick, "Could not find factoid '{}' in my database.".format(factoid))

    def on_command(self, target, nick, command, commandtext, mod, admin):

        if command == "isfactoid" or command == "factoid":
            if not commandtext:
                self.notice(nick, "Usage: isfactoid <factoid>")

            channel = self.factoid_getchannel(target, commandtext)
            commandtext = commandtext.replace(" -global", "").strip()

            if not self.factoid_isvalid(commandtext):
                self.notice(nick, "Factoid triggers may only contain A-Z and /")
            elif self.factoid_exists(commandtext):
                self.message(target, nick, self.factoid_getinfo(commandtext, channel))
            else:
                self.notice(nick, "Factoid '{}' does not exist in the database.".format(commandtext))

            return True

        if mod:
            if command == "addfactoid":
                if not commandtext or len(commandtext.split()) < 1:
                    return self.notice(nick, "Please select a factoid trigger with response to add.")

                channel = self.factoid_getchannel(target, commandtext)
                commandtext = commandtext.replace(" -global", "").strip()

                ct = commandtext.split()
                factoid_trigger = ct[0]
                factoid_response = " ".join(ct[1:])

                if len(ct) < 4:
                    self.notice(nick, "Factoid response '{}' is too short.".format(factoid_response))
                elif not self.factoid_isvalid(factoid_trigger):
                    self.notice(nick, "Factoid triggers may only contain A-Z and /")
                elif self.factoid_exists(factoid_trigger, channel):
                    self.notice(nick, "Factoid trigger '{}' already exists. Use editfactoid instead."
                                      .format(factoid_trigger))
                else:
                    self.factoid_add(nick, factoid_trigger, factoid_response, channel)
                    self.message(target, nick, "Response was added under '{}'".format(factoid_trigger))

                return True

            if command == "editfactoid":
                if not commandtext or len(commandtext.split()) < 1:
                    return self.notice(nick, "Please select a factoid trigger with response to edit.")

                channel = self.factoid_getchannel(target, commandtext)
                commandtext = commandtext.replace(" -global", "").strip()

                ct = commandtext.split()
                factoid_trigger = ct[0]
                factoid_response = " ".join(ct[1:])

                if len(ct) < 4:
                    self.notice(nick, "Factoid response '{}' is too short.".format(factoid_response))
                elif not self.factoid_isvalid(factoid_trigger):
                    self.notice(nick, "Factoid triggers may only contain A-Z and /")
                elif not self.factoid_exists(factoid_trigger):
                    self.notice(nick, "Factoid trigger '{}' doesn't exist. Use addfactoid instead."
                                      .format(factoid_trigger))
                else:
                    self.factoid_del(factoid_trigger, channel)
                    self.factoid_add(nick, factoid_trigger, factoid_response, channel)
                    self.message(target, nick, "Response was edited under '{}'".format(factoid_trigger))

                return True

            if command == "delfactoid":
                if not commandtext:
                    self.notice(nick, "Please select a factoid trigger to delete")

                channel = self.factoid_getchannel(target, commandtext)
                commandtext = commandtext.replace(" -global", "").strip()

                if not self.factoid_isvalid(commandtext):
                    self.notice(nick, "Factoid triggers may only contain A-Z and /")
                elif self.factoid_exists(commandtext):
                    private_exists = self.factoid_exists(commandtext, channel)

                    self.factoid_del(commandtext, channel)

                    if private_exists and channel and not self.factoid_exists(commandtext, channel):
                        self.message(target, nick, "Private Factoid ({}) with trigger '{}' was deleted."
                                                   .format(channel, commandtext))
                    elif not channel and not self.factoid_exists(commandtext):
                        self.message(target, nick, "Global Factoid with trigger '{}' was deleted.".format(commandtext))
                    else:
                        self.message(target, nick, "Error: Factoid with trigger '{}' still exists."
                                                   .format(commandtext))

                else:
                    self.notice(nick, "Factoid '{}' does not exist.".format(commandtext))

                return True

            if command == "countfactoid" or command == "countfactoids":
                channel = self.factoid_getchannel(target, commandtext)
                if channel:
                    count = self.factoid_count(channel)
                    return self.message(target, nick,
                                        "There {} currently {} response{} registered in my database for {}."
                                        .format("is" if count == 1 else "are", count,
                                                "" if count == 1 else "s", channel))
                else:
                    count = self.factoid_count()
                    return self.message(target, nick, "There {} currently {} response{} registered in my database."
                                        .format("is" if count == 1 else "are", count, "" if count == 1 else "s"))

        return False

    def factoid_getchannel(self, channel, params=None):
        globally = params and "-global" in params
        if channel.startswith("#") and not self.module_data["global_factoids"] and not globally:
            return channel

        return None

    def factoid_getresponse(self, factoid, channel=None):
        factoid = factoid.lower()
        response = ""
        found = False

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            if not channel:
                result = (c.execute("SELECT response FROM factoids WHERE factoid = ?", [factoid])
                          .fetchone())
            else:
                result = (c.execute("SELECT response FROM factoids WHERE factoid = ? AND channel = ?",
                          [factoid, channel]).fetchone())

            if result and len(result) == 1:
                response = result[0]
                found = True
            else:
                response = "Factoid '{}' was not found in the database".format(factoid)

            conn.close()
        except sqlite3.Error as e:
            response = "factoid_getresponse({}) error: {}".format(factoid, str(e))
            self.error(response)

        if not found and channel and self.factoid_exists(factoid):  # get the global factoid instead if exists.
            return self.factoid_getresponse(factoid)

        return response

    def factoid_getinfo(self, factoid, channel=None):
        factoid = factoid.lower()
        response = ""
        found = False

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            if not channel:
                result = (c.execute("SELECT adder, channel, timestamp, response FROM factoids WHERE factoid = ?",
                          [factoid]).fetchone())
            else:
                result = c.execute("SELECT adder, channel, timestamp, response FROM factoids "
                                   "WHERE factoid = ? AND channel = ?", [factoid, channel]).fetchone()

            if result and len(result) > 2:
                globalfact = "as global factoid" if result[1] == "global" else "for {}".format(result[1])
                response = ("Factoid '{}' was added by {} {} on {} with response: {}"
                            .format(factoid, result[0], globalfact, result[2], result[3]))
                found = True
            else:
                response = "Factoid '{}' was not found in the database".format(factoid)

            conn.close()
        except sqlite3.Error as e:
            response = "factoid_getinfo({}): {}".format(factoid, str(e))
            self.error(response)

        if not found and channel and self.factoid_exists(factoid):  # get the global factoid instead if exists.
            response = self.factoid_getinfo(factoid)

        return response

    def factoid_exists(self, factoid, channel=None):
        factoid = factoid.lower()
        exists = False

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            if not channel:
                result = c.execute("SELECT adder FROM factoids WHERE factoid = ?", [factoid])
            else:
                result = c.execute("SELECT adder FROM factoids WHERE factoid = ? AND channel = ?", [factoid, channel])

            if result.fetchone():
                exists = True

            conn.close()
        except sqlite3.Error as e:
            self.error("factoid_exists({}) error: {}".format(factoid, str(e)))

        return exists

    def factoid_isvalid(self, factoid):
        return factoid.replace("/", "").isalpha()

    def factoid_count(self, channel=None):
        rows = 0

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            if channel:
                rows = len(c.execute("SELECT count(factoid) FROM factoids WHERE channel = ?", [channel]).fetchall())
            else:
                rows = len(c.execute("SELECT count(factoid) FROM factoids").fetchall())

            conn.close()
        except sqlite3.Error as e:
            self.error("factoid_count() error: {}".format(str(e)))

        return rows

    def factoid_del(self, factoid_trigger, channel=None):
        factoid_trigger = factoid_trigger.lower()
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            if not channel:
                c.execute("DELETE FROM factoids WHERE factoid = ?", [factoid_trigger])
            else:
                c.execute("DELETE FROM factoids WHERE factoid = ? AND channel = ?", [factoid_trigger, channel])

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.error("factoid_del({}) error: {}".format(factoid_trigger, str(e)))

    def factoid_add(self, adder, factoid_trigger, factoid_response, channel=None):
        factoid_trigger = factoid_trigger.lower()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            if not channel:
                c.execute("INSERT INTO factoids (adder, channel, timestamp, factoid, response) VALUES (?, ?, ?, ?, ?)",
                          [adder, "global", timestamp, factoid_trigger, factoid_response])
            else:
                c.execute("INSERT INTO factoids (adder, channel, timestamp, factoid, response) VALUES (?, ?, ?, ?, ?)",
                          [adder, channel, timestamp, factoid_trigger, factoid_response])

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.error("factoid_add({}, {}, {}) error: {}".format(adder, factoid_trigger, factoid_response, str(e)))

    def factoid_isrequest(self, line):
        """What to check for to validate user is requesting a bot factoid"""
        linelen = len(line.split())

        if linelen > 1 and linelen < 4 and (line.startswith("$$") or line.startswith("$?")):
            return True
        return False

    def factoid_isaltrequest(self, word):
        """What to check for to validate user is requesting a bot factoid - alternative syntax"""

        if word.startswith("[[") and word.endswith("]]"):
            return True
        return False

    def factoid_make_db(self):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS factoids "
                      "(adder TEXT, channel TEXT, timestamp TEXT, factoid TEXT, response TEXT)")
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.error("factoid_make_db() error: Failed to create database factoids.db: {}".format(str(e)))
