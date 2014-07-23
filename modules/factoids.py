"""
factoids.py by Zarthus
Licensed under MIT

factoid responses.
"""

from core import moduletemplate
from tools import formatter
from tools import validator

import os
import time
import sqlite3


class Factoids(moduletemplate.BotModule):
    """Factoids: brief answers to frequently asked questions and other responses."""

    def on_module_load(self):
        self.colformat = formatter.IrcFormatter()
        self.validator = validator.Validator()

        self.db_file = os.path.join(self.db_dir, "factoids.db")
        self.factoid_make_db()

    def on_privmsg(self, channel, nick, message):
        words = message.split()

        for word in words:
            if self.factoid_isrequest(word):
                # Slice off [[ ]]
                factoid = word[2:-2]
                target = None

                # check if it was targeting a name [[name:factoid]]
                if ":" in factoid:
                    split = factoid.split(":")
                    target = split[0]

                    if len(split) > 1:
                        factoid = split[1]

                    if not self.validator.nickname(target):
                        target = None
                        factoid = split[0]

                if self.factoid_exists(factoid):
                    self.reply_channel(channel, target, self.colformat.parse(self.factoid_getresponse(factoid)))
                else:
                    self.reply_notice(nick, "Could not find factoid '{}' in my database.".format(factoid))

    def on_command(self, channel, nick, command, commandtext, mod=False, admin=False):

        if command == "isfactoid" or command == "factoid":
            if not self.factoid_isvalid(commandtext):
                self.reply_notice(nick, "Factoid triggers may only contain A-Z and /")
            elif self.factoid_exists(commandtext):
                self.reply_channel(channel, nick, self.factoid_getinfo(commandtext))
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
                    self.reply_notice(nick, "Factoid trigger '{}' already exists.".format(factoid_trigger))
                else:
                    self.factoid_add(nick, factoid_trigger, factoid_response)
                    self.reply_channel(channel, nick, "Response was added under '{}'".format(factoid_trigger))

                return True

            if command == "editfactoid":
                if not commandtext or len(commandtext.split()) < 1:
                    return self.reply_notice(nick, "Please select a factoid trigger with response to edit.")

                ct = commandtext.split()
                factoid_trigger = ct[0]
                factoid_response = " ".join(ct[0:])

                if len(ct) < 4:
                    self.reply_notice(nick, "Factoid response '{}' is too short.".format(factoid_response))
                elif not self.factoid_isvalid(factoid_trigger):
                    self.reply_notice(nick, "Factoid triggers may only contain A-Z and /")
                elif not self.factoid_exists(factoid_trigger):
                    self.reply_notice(nick, "Factoid trigger '{}' doesn't exist.".format(factoid_trigger))
                else:
                    self.factoid_del(factoid_trigger)
                    self.factoid_add(nick, factoid_trigger, factoid_response)
                    self.reply_channel(channel, nick, "Response was edited under '{}'".format(factoid_trigger))

                return True

            if command == "delfactoid":

                if not commandtext:
                    self.reply_notice(nick, "Please select a factoid trigger to delete")
                if not self.factoid_isvalid(commandtext):
                    self.reply_notice(nick, "Factoid triggers may only contain A-Z and /")
                elif self.factoid_exists(commandtext):
                    self.factoid_del(commandtext)
                    self.reply_channel(channel, nick, "Factoid with trigger '{}' was deleted.".format(factoid_trigger))
                else:
                    self.reply_notice(nick, "Factoid '{}' does not exist.".format(commandtext))

                return True

            if command == "countfactoid" or command == "countfactoids":
                return self.reply_channel(channel, nick, "There are currently {} responses registered in my database."
                                                         .format(self.factoid_count()))

        return False

    def factoid_getresponse(self, factoid):
        response = ""

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = (c.execute("SELECT response FROM factoids WHERE factoid = ?", [factoid.lower()])
                      .fetchone())

            if len(result) == 1:
                response = result[0]
            else:
                response = "Factoid '{}' was not found in the database".format(factoid)

            conn.close()
        except sqlite3.Error as e:
            # TODO: Log
            response = "An error has occured: {}".format(str(e))

        return response

    def factoid_getinfo(self, factoid):
        response = ""

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = (c.execute("SELECT adder, timestamp, response FROM factoids WHERE factoid = ?", [factoid.lower()])
                      .fetchone())

            if len(result) > 2:
                response = ("Factoid '{}' was added by {} on {} with response: {}"
                            .format(factoid, result[0], result[1], result[2]))
            else:
                response = "Factoid '{}' was not found in the database".format(factoid)

            conn.close()
        except sqlite3.Error as e:
            # TODO: Log
            response = "An error has occured: {}".format(str(e))

        return response

    def factoid_exists(self, factoid):
        exists = False

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = c.execute("SELECT adder FROM factoids WHERE factoid = ?", [factoid.lower()])

            if result.fetchone():
                exists = True

            conn.close()
        except sqlite3.Error as e:
            # TODO: log
            print("factoid_exists({}) error: {}".format(factoid, str(e)))

        return exists

    def factoid_isvalid(self, factoid):
        return factoid.replace("/", "").isalpha()

    def factoid_count(self):
        rows = 0

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            rows = c.execute("SELECT count(factoid) FROM factoids").rowcount

            conn.close()
        except sqlite3.Error as e:
            # TODO: Log
            print("factoid_count() error: {}".format(str(e)))

        return rows

    def factoid_del(self, factoid_trigger):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("DELETE FROM factoids WHERE factoid = ?", [factoid.lower()])

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            # TODO: log
            print("factoid_del({}) error: {}".format(factoid_trigger, str(e)))

    def factoid_add(self, adder, factoid_trigger, factoid_response):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("INSERT INTO factoids (adder, timestamp, factoid, response) VALUES (?, ?, ?, ?)",
                      [adder, timestamp, factoid_trigger.lower(), factoid_response])

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            # TODO: log
            print("factoid_add({}, {}, {}) error: {}".format(adder, factoid_trigger, factoid_response, str(e)))

    def factoid_isrequest(self, word):
        """What to check for to validate user is requesting a bot factoid"""

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
            # TODO: Log
            print("factoid_make_db() error: Failed to create database factoids.db: {}".format(str(e)))
