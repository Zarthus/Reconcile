"""
seen.py by Zarthus
Licensed under MIT

Check when an user was last seen (according to the bots database).
"""

from core import moduletemplate
from tools import duration
from tools import validator

import os
import random
import sqlite3
import time


class Seen(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("seen", "<nickname>",
                              ("Return when (or if) <nickname> was seen by the bot. This data may not be fully "
                               "accurate because not everyone joins the channels the bot is in."), self.PRIV_NONE)

        self.db_file = os.path.join(self.db_dir, "seen.db")
        self.validator = validator.Validator()

        self.make_seen_db()

        if "store_message" not in self.module_data:
            # It's safer (sql injections), more resource efficient (less to store), and less privacy-infringing
            # to not store messages.
            self.module_data["store_message"] = False

    def on_privmsg(self, target, nick, message):
        if self.module_data["store_message"]:
            if len(message) > 50:
                message = message[:50] + ".."

            self.store_seen(nick, "sending a PRIVMSG to {} saying: {}".format(target, message))
        else:
            self.store_seen(nick, "sending a PRIVMSG to {}".format(target))

    def on_action(self, target, nick, action):
        if self.module_data["store_message"]:
            if len(action) > 50:
                action = action[:50] + ".."

            self.store_seen(nick, "sending a CTCP ACTION to {} saying: {}".format(target, action))
        else:
            self.store_seen(nick, "sending a CTCP ACTION to {}".format(target))

    def on_join(self, nick, channel):
        self.store_seen(nick, "joining {}".format(channel))

    def on_part(self, nick, channel, message):
        if self.module_data["store_message"] and message:
            if len(message) > 50:
                message = message[:50] + ".."

            self.store_seen(nick, "parting {} with message: {}".format(channel, message))
        else:
            self.store_seen(nick, "parting {}".format(channel))

    def on_kick(self, nick, channel, knick, reason):
        if self.module_data["store_message"] and reason:
            if len(reason) > 50:
                reason = reason[:50] + ".."

            self.store_seen(nick, "kicking {} from {} with reason: {}".format(knick, channel, reason))
            self.store_seen(knick, "being kicked from {} by {} with reason: {}".format(channel, nick, reason))
        else:
            self.store_seen(nick, "kicking somebody from {}".format(channel))
            self.store_seen(knick, "being kicked from {}".format(channel))

    def on_quit(self, nick, message):
        if self.module_data["store_message"] and message:
            if len(message) > 50:
                message = message[:50] + ".."

            self.store_seen(nick, "quitting IRC with message: {}".format(message))
        else:
            self.store_seen(nick, "quitting IRC")

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "seen":
            if not commandtext:
                return self.notice(nick, "Usage: seen <nickname>")

            if not self.validator.nickname(commandtext):
                return self.notice(nick, "Nickname is not a valid nickname for IRC.")

            if commandtext.lower() == nick.lower():
                responses = [
                    "Have you been looking into the mirror lately, $(nick)?",
                    "Have I seen $(nick)..? Hmm. Nope, never heard of this person!",
                    "Have you seen $(nick), $(nick)?",
                    "Why is it this always seems to be an 'easter egg' in IRC bots?",
                    "I don't know, and I don't care."
                ]

                return self.message(target, None, random.choice(responses).replace("$(nick)", nick))

            if not self.was_seen(commandtext):
                return self.message(target, nick, "I have not seen '{}' before.".format(commandtext))

            seendata = self.get_seen(commandtext)
            if seendata:
                return self.message(target, nick, seendata)
            return self.message(target, nick, "I could not look up data for '{}'.".format(commandtext))
        return False

    def get_userhost_from_nick(self, nick):
        """
        We cannot be certain the host/user exists because some events are called on quits/parting.
        Regardless, we try our best to try and get an users user@host.
        """
        uinfo = self.getUserData(nick)

        user = None
        host = None

        if uinfo:
            user = uinfo["user"] if "user" in uinfo else None
            host = uinfo["host"] if "host" in uinfo else None

        if not host:
            host = "?"
        if not user:
            user = "?"

        return "{}@{}".format(user, host)

    def was_seen(self, nickname):
        if not self.validator.nickname(nickname):
            self.logger.notice("seen: Tried to get wasseen data from invalid nickname {}".format(nickname))
            return False

        seen = False
        nickname = nickname.lower()
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = c.execute("SELECT nick FROM seen WHERE lower(nick) = ?", [nickname])

            if result.fetchone():
                seen = True

            conn.close()
        except sqlite3.Error as e:
            self.logger.error("was_seen({}) error: {}".format(nickname, str(e)))

        return seen

    def get_seen(self, nickname):
        if not self.validator.nickname(nickname):
            self.logger.notice("seen: Tried to get seen data from invalid nickname {}".format(nickname))
            return False

        nickname = nickname.lower()
        response = ""

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = c.execute("SELECT * FROM seen WHERE lower(nick) = ?", [nickname]).fetchone()

            if len(result) > 4:
                response = ("{} ({}) was last seen on {} ({} ago) {}"
                            .format(result[0], result[1], result[2],
                                    duration.timesincetimestamp(int(result[3])), result[4]))

            conn.close()
        except sqlite3.Error as e:
            self.logger.error("get_seen({}) error: {}".format(nickname, str(e)))

        return response

    def store_seen(self, nickname, data):
        if not self.validator.nickname(nickname):
            self.logger.notice("seen: Tried to store invalid nickname {}".format(nickname))
            return False

        host = self.get_userhost_from_nick(nickname)
        timestamp = time.strftime("%d %B, %Y - %H:%M:%S %Z")
        unix_timestamp = int(time.time())

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO seen (nick, host, timestamp, unix_timestamp, description) "
                      "VALUES (?, ?, ?, ?, ?)", [nickname, host, timestamp, unix_timestamp, data])

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error("store_seen({}, {}) error: {}".format(nickname, data, str(e)))

    def make_seen_db(self):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS seen "
                      "(nick TEXT UNIQUE, host TEXT, timestamp TEXT, unix_timestamp TEXT, description TEXT)")
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error("make_seen_db() error: Failed to create database seen.db: {}".format(str(e)))
