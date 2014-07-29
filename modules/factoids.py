"""
factoids.py by Zarthus
Licensed under MIT

Factoids: brief answers to frequently asked questions and other responses.
"""

from core import moduletemplate
from tools import formatter
from tools import validator

import os
import time
import sqlite3


class Factoids(moduletemplate.BotModule):

    def on_module_load(self):
        self.colformat = formatter.IrcFormatter()
        self.validator = validator.Validator()

        self.db_file = os.path.join(self.db_dir, "factoids.db")
        self.factoid_make_db()

        self.register_command("isfactoid", "<factoid>", "Check if <factoid> exists and return information if it does.",
                              self.PRIV_NONE, ["factoid"])
        self.register_command("addfactoid", "<factoid> <response>",
                              "Adds <factoid> with <response> to the factoid database.", self.PRIV_MOD)
        self.register_command("editfactoid", "<factoid> <new response>",
                              "Edits <factoid> with <new response>", self.PRIV_MOD)
        self.register_command("delfactoid", "<factoid>", "Deletes <factoid> from the factoid database.", self.PRIV_MOD)
        self.register_command("countfactoid", None, "Returns the number of factoids in the database.",
                              self.PRIV_MOD, ["countfactoids"])

    def on_privmsg(self, target, nick, message):
        words = message.split()

        if self.factoid_isrequest(message):
            if message.startswith("$$"):
                factoid = words[1]

                if not self.factoid_isvalid(factoid):
                    self.reply_notice(nick, "Factoid request '{}' is an invalid factoid trigger name.".format(factoid))
                elif self.factoid_exists(factoid):
                    self.reply_target(target, None, self.colformat.parse(self.factoid_getresponse(factoid)))
                else:
                    self.reply_notice(nick, "Could not find factoid '{}' in my database.".format(factoid))
            else:
                if len(words) < 3:
                    return self.reply_notice(nick, "Syntax error, usage: $? <nick> <factoid>")
                ftarget = words[1]
                factoid = words[2]

                if not self.factoid_isvalid(factoid):
                    self.reply_notice(nick, "Factoid request '{}' is an invalid factoid trigger name.".format(factoid))
                elif self.factoid_exists(factoid):
                    self.reply_target(target, None, "{}: {}".format(ftarget, 
                                                             self.colformat.parse(self.factoid_getresponse(factoid))))
                else:
                    self.reply_notice(nick, "Could not find factoid '{}' in my database.".format(factoid))

            return True
        else:
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
                        self.reply_target(target, ftarget, self.colformat.parse(self.factoid_getresponse(factoid)))
                    else:
                        self.reply_notice(nick, "Could not find factoid '{}' in my database.".format(factoid))

    def on_command(self, target, nick, command, commandtext, mod, admin):

        if command == "isfactoid" or command == "factoid":
            if not self.factoid_isvalid(commandtext):
                self.reply_notice(nick, "Factoid triggers may only contain A-Z and /")
            elif self.factoid_exists(commandtext):
                self.reply_target(target, nick, self.factoid_getinfo(commandtext))
            else:
                self.reply_notice(nick, "Factoid '{}' does not exist in the database.".format(commandtext))

            return True

        if mod:
            if command == "addfactoid":
                if not commandtext or len(commandtext.split()) < 1:
                    return self.reply_notice(nick, "Please select a factoid trigger with response to add.")

                ct = commandtext.split()
                factoid_trigger = ct[0]
                factoid_response = " ".join(ct[1:])

                if len(ct) < 4:
                    self.reply_notice(nick, "Factoid response '{}' is too short.".format(factoid_response))
                elif not self.factoid_isvalid(factoid_trigger):
                    self.reply_notice(nick, "Factoid triggers may only contain A-Z and /")
                elif self.factoid_exists(factoid_trigger):
                    self.reply_notice(nick, "Factoid trigger '{}' already exists. Use editfactoid instead."
                                            .format(factoid_trigger))
                else:
                    self.factoid_add(nick, factoid_trigger, factoid_response)
                    self.reply_target(target, nick, "Response was added under '{}'".format(factoid_trigger))

                return True

            if command == "editfactoid":
                if not commandtext or len(commandtext.split()) < 1:
                    return self.reply_notice(nick, "Please select a factoid trigger with response to edit.")

                ct = commandtext.split()
                factoid_trigger = ct[0]
                factoid_response = " ".join(ct[1:])

                if len(ct) < 4:
                    self.reply_notice(nick, "Factoid response '{}' is too short.".format(factoid_response))
                elif not self.factoid_isvalid(factoid_trigger):
                    self.reply_notice(nick, "Factoid triggers may only contain A-Z and /")
                elif not self.factoid_exists(factoid_trigger):
                    self.reply_notice(nick, "Factoid trigger '{}' doesn't exist. Use addfactoid instead."
                                            .format(factoid_trigger))
                else:
                    self.factoid_del(factoid_trigger)
                    self.factoid_add(nick, factoid_trigger, factoid_response)
                    self.reply_target(target, nick, "Response was edited under '{}'".format(factoid_trigger))

                return True

            if command == "delfactoid":
                if not commandtext:
                    self.reply_notice(nick, "Please select a factoid trigger to delete")
                if not self.factoid_isvalid(commandtext):
                    self.reply_notice(nick, "Factoid triggers may only contain A-Z and /")
                elif self.factoid_exists(commandtext):
                    self.factoid_del(commandtext)
                    self.reply_target(target, nick, "Factoid with trigger '{}' was deleted.".format(commandtext))
                else:
                    self.reply_notice(nick, "Factoid '{}' does not exist.".format(commandtext))

                return True

            if command == "countfactoid" or command == "countfactoids":
                return self.reply_target(target, nick, "There are currently {} responses registered in my database."
                                                       .format(self.factoid_count()))

        return False

    def factoid_getresponse(self, factoid):
        factoid = factoid.lower()
        response = ""

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = (c.execute("SELECT response FROM factoids WHERE factoid = ?", [factoid])
                      .fetchone())

            if len(result) == 1:
                response = result[0]
            else:
                response = "Factoid '{}' was not found in the database".format(factoid)

            conn.close()
        except sqlite3.Error as e:
            response = "factoid_getresponse({}) error: {}".format(factoid, str(e))
            self.logger.error(response)

        return response

    def factoid_getinfo(self, factoid):
        factoid = factoid.lower()
        response = ""

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = (c.execute("SELECT adder, timestamp, response FROM factoids WHERE factoid = ?", [factoid])
                      .fetchone())

            if len(result) > 2:
                response = ("Factoid '{}' was added by {} on {} with response: {}"
                            .format(factoid, result[0], result[1], result[2]))
            else:
                response = "Factoid '{}' was not found in the database".format(factoid)

            conn.close()
        except sqlite3.Error as e:
            response = "factoid_getinfo({}): {}".format(factoid, str(e))
            self.logger.error(response)

        return response

    def factoid_exists(self, factoid):
        factoid = factoid.lower()
        exists = False

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = c.execute("SELECT adder FROM factoids WHERE factoid = ?", [factoid])

            if result.fetchone():
                exists = True

            conn.close()
        except sqlite3.Error as e:
            self.logger.error("factoid_exists({}) error: {}".format(factoid, str(e)))

        return exists

    def factoid_isvalid(self, factoid):
        return factoid.replace("/", "").isalpha()

    def factoid_count(self):
        rows = 0

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            rows = len(c.execute("SELECT count(factoid) FROM factoids").fetchall())

            conn.close()
        except sqlite3.Error as e:
            self.logger.error("factoid_count() error: {}".format(str(e)))

        return rows

    def factoid_del(self, factoid_trigger):
        factoid_trigger = factoid_trigger.lower()
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("DELETE FROM factoids WHERE factoid = ?", [factoid_trigger])

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error("factoid_del({}) error: {}".format(factoid_trigger, str(e)))

    def factoid_add(self, adder, factoid_trigger, factoid_response):
        factoid_trigger = factoid_trigger.lower()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("INSERT INTO factoids (adder, timestamp, factoid, response) VALUES (?, ?, ?, ?)",
                      [adder, timestamp, factoid_trigger, factoid_response])

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error("factoid_add({}, {}, {}) error: {}"
                              .format(adder, factoid_trigger, factoid_response, str(e)))

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
                      "(adder TEXT, timestamp TEXT, factoid TEXT UNIQUE, response TEXT)")
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error("factoid_make_db() error: Failed to create database factoids.db: {}".format(str(e)))
