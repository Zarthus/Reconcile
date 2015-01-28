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

Tell by Zarthus
Licensed under MIT

Tell the bot to remember something. When target is active, return message.
"""

from core import moduletemplate
from tools import duration
from tools import validator

import sqlite3
import os
import time


class Tell(moduletemplate.BotModule):

    def on_module_load(self):
        self.db_file = os.path.join(self.db_dir, "{}_tell.db".format(self.network_name))

        self.register_command("tell", "<nickname> <message>",
                              "Once <nickname> appears online (by sending a message to a channel I am in), "
                              "message them with <message>", self.PRIV_NONE, ["note"])
        self.register_command("telldel", "<nickname | *>",
                              "Delete all pending messages for <nickname>, or all if * is specified.",
                              self.PRIV_NONE, ["deltell", "delnote"])
        self.register_command("tellslist", None,
                              "Show if you have any pending messages or not, if you do, they are sent to your query.",
                              self.PRIV_NONE, ["listtells", "listtell", "notelist", "noteslist", "listnotes"])
        self.register_command("tellhas", "[nickname]", "Check if [nickname] has any pending tells.",
                              self.PRIV_NONE, ["hastell", "hastells", "hasnote"])
        self.register_command("tells", None, "Count the number of active tells in the database.",
                              self.PRIV_MOD, ["notes"])

        if "max_tells" not in self.module_data:
            self.module_data["max_tells"] = 5

        self.hastells = {}

        self.tell_make_db()
        self.validator = validator.Validator()

    def on_privmsg(self, target, nick, message):
        if self.has_tells(nick):
            self.show_tells(nick)

    def on_join(self, nick, channel):
        if nick.lower() not in self.hastells:
            if self.has_tells(nick):
                count = self.tell_count(nick)
                self.message(nick, None, "Hello {}! You seem to have $(bold){}$(bold) pending message{}. "
                                         "To view these messages, reply to my query with 'listtells' or speak in a "
                                         "channel we share.".format(nick, count, "s" if count != 1 else ""), True)

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command in ["listtells", "listtell", "tellslist", "notelist", "noteslist", "listnotes"]:
            if self.has_tells(nick):
                return self.show_tells(nick)
            else:
                return self.notice(nick, "You do not have any pending messages.")

        if command in ["hastell", "hastells", "tellhas", "hasnote", "hasnotes", "notehas"]:
            targ = commandtext
            if not targ:
                targ = nick

            if not self.validator.nickname(targ):
                return self.notice(nick, "'{}' is not a valid IRC nickname.".format(targ))

            if self.has_tells(targ):
                return self.message(target, nick, "{} has pending messages.".format(targ))
            return self.message(target, nick, "{} has no pending messages.".format(targ))

        if command in ["tell", "note"]:
            ct = commandtext.split()
            if not commandtext or len(ct) < 2:
                return self.notice(nick, "Usage: tell <nickname> <message>")

            to = ct[0]
            msg = " ".join(ct[1:])

            if not self.validator.nickname(to):
                return self.notice(nick, "'{}' is an invalid nickname.".format(to))

            if to == self._conn.currentnick:
                return self.notice(nick, "I cannot set tells for myself.")

            if self.tell_passes_limit(nick):
                return self.notice(nick, "You cannot set anymore tells. "
                                         "Use deltell <nickname | *> to delete existing tells")
            if self.tell_passes_limit(to, False):
                return self.notice(nick, "{} cannot receive anymore tells.".format(to))

            if self.tell_exists(nick, to):
                return self.notice(nick, "You are already sending a message to {}. "
                                         "Use 'deltell {}' to be able send a new message.".format(to, to))

            success = self.tell_store(nick, to, msg)
            if success:
                return self.message(target, nick, "I will let {} know they have a pending message.".format(to))
            return self.message(target, nick, "I was unable to add a message for {}.".format(to))

        if command in ["deltell", "telldel", "delnote", "notedel"]:
            if not commandtext:
                return self.notice(nick, "Usage: deltell <nickname | *>")

            if commandtext == "*":
                self.tell_delete_all(nick)
                return self.message(target, nick, "Deleted all pending messages sent by you.")

            if not self.validator.nickname(commandtext):
                return self.notice(nick, "'{}' is an invalid nickname.".format(commandtext))

            if not self.has_tells(commandtext):
                return self.notice(nick, "{} has no pending messages.".format(commandtext))

            if not self.tell_count(nick, commandtext):
                return self.notice(nick, "{} has no pending messages from you.".format(commandtext))

            success = self.tell_delete(nick, commandtext)
            if success:
                return self.message(target, nick, "Deleted all messages to {} from you.".format(commandtext))
            return self.message(target, nick, "Was unable to delete pending messages sent by you.")

        if mod:
            if command in ["notes", "tells"]:
                count = self.tell_count("*")
                return self.message(target, nick, "There are {} pending message{} in my database."
                                                  .format(count, "s" if count != 1 else ""))
        return False

    def show_tells(self, nick):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = c.execute("SELECT sender, message, timestamp, unix_timestamp FROM tell WHERE "
                               "lower(recipient) = ?", [nick.lower()]).fetchall()

            for msg in result:
                self.message(nick, None, "$(bold){}$(clear) left you a message: {} - Sent on {} ({} ago)"
                                         .format(msg[0], msg[1], msg[2],
                                                 duration.timesincetimestamp(int(msg[3]))), True)

                if msg[0] == "$(lime)TellModule":  # We don't want this kind of recursion.
                    continue

                if nick.lower() != msg[0].lower():
                    udata = self.getUserData(msg[0])  # Let the sender know message has been sent if they're online.
                    if udata:
                        self.message(msg[0], None, "Delivered message '{}' to {} sent on {}."
                                                   .format(msg[1], nick, msg[2]))
                    else:
                        # Manually add a new entry to the database to let the user know their message was delivered.
                        sender = "$(lime)TellModule"
                        rcvmsg = ("Your message '{}' to {} has been delivered (Sent by you on: {})."
                                  .format(msg[1], nick, msg[2]))
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S %Z")
                        unix_timestamp = int(time.time())
                        c.execute("INSERT INTO tell (sender, recipient, message, timestamp, unix_timestamp) "
                                  "VALUES (?, ?, ?, ?, ?)", [sender, msg[0], rcvmsg, timestamp, unix_timestamp])
                        self.hastells[msg[0].lower()] = True

            c.execute("DELETE FROM tell WHERE lower(recipient) = ?", [nick.lower()])
            self.hastells[nick.lower()] = False

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.error("show_tells({}) error: {}".format(nick, str(e)))
            return False
        return True

    def has_tells(self, to):
        to = to.lower()
        if to in self.hastells:
            return self.hastells[to]

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = c.execute("SELECT timestamp FROM tell WHERE lower(recipient) = ?",
                               [to]).fetchone()
            if result and len(result) >= 1:
                self.hastells[to] = True
            else:
                self.hastells[to] = False
            conn.close()
        except sqlite3.Error as e:
            self.error("has_tells({}) error: {}".format(to, str(e)))
            return False

        if to in self.hastells:  # This should always be set, but the extra security if doesn't hurt.
            return self.hastells[to]
        return False

    def tell_exists(self, sender, to):
        exists = False
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = c.execute("SELECT timestamp FROM tell WHERE lower(sender) = ? and lower(recipient) = ?",
                               [sender.lower(), to.lower()]).fetchone()
            if result and len(result) >= 1:
                exists = True
            conn.close()
        except sqlite3.Error as e:
            self.error("tell_exists({}, {}) error: {}".format(sender, to, str(e)))
            return False

        return exists

    def tell_passes_limit(self, sender, send=True):
        """
        Check if somebody is sending too many tells.
        Sender: string, sender or receiver nick.
        Send: Is it a sender, or a receiver.

        Send should be set to false if you want to check if they have too many pending messages,
        otherwise if they are sending too many.
        """

        passedlimit = False
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            result = None
            if send:
                result = c.execute("SELECT count(timestamp) FROM tell WHERE lower(sender) = ?",
                                   [sender.lower()]).fetchone()
            else:
                result = c.execute("SELECT count(timestamp) FROM tell WHERE lower(recipient) = ?",
                                   [sender.lower()]).fetchone()

            if result[0] >= self.module_data["max_tells"]:
                passedlimit = True
            conn.close()
        except sqlite3.Error as e:
            self.error("tell_passes_limit({}, {}) error: {}".format(sender, str(send), str(e)))
            return False

        return passedlimit

    def tell_count(self, sender, to=None):
        count = 0
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = None

            if sender == "*":
                result = c.execute("SELECT count(timestamp) FROM tell WHERE 1").fetchone()
            elif to:
                result = c.execute("SELECT count(timestamp) FROM tell WHERE lower(sender) = ? and "
                                   "lower(recipient) = ?", [sender.lower(), to.lower()]).fetchone()
            else:
                result = c.execute("SELECT count(timestamp) FROM tell WHERE lower(sender) = ?",
                                   [sender.lower()]).fetchone()

            count = result[0]
            conn.close()
        except sqlite3.Error as e:
            self.error("tell_list({}) error: {}".format(sender, str(e)))
            return False
        return count

    def tell_store(self, sender, to, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S %Z")
        unix_timestamp = int(time.time())
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("INSERT INTO tell (sender, recipient, message, timestamp, unix_timestamp) "
                      "VALUES (?, ?, ?, ?, ?)", [sender, to, message, timestamp, unix_timestamp])
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.error("tell_store({}, {}, {}) error: {}".format(sender, to, message, str(e)))
            return False

        self.hastells[to.lower()] = True
        return True

    def tell_delete(self, sender, to):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("DELETE FROM tell WHERE lower(sender) = ? and lower(recipient) = ?",
                      [sender.lower(), to.lower()])
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.error("tell_delete({}, {}) error: {}".format(sender, to, str(e)))
            return False

        self.hastells[to.lower()] = False
        return True

    def tell_delete_all(self, sender):
        """Deletes all pending tells from user."""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("DELETE FROM tell WHERE lower(sender) = ?", [sender.lower()])
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.error("tell_delete_all({}) error: {}".format(sender, str(e)))
            return False

        self.hastells[sender.lower()] = False
        return True

    def tell_make_db(self):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS tell "
                      "(sender TEXT, recipient TEXT, message TEXT, timestamp TEXT, unix_timestamp TEXT)")
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.error("tell_make_db() error: Failed to create database tell.db: {}".format(str(e)))
