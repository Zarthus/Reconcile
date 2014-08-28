"""
Quote by Zarthus
Licensed under MIT

Remember memorable quotes!
"""

from core import moduletemplate

import sqlite3
import os
import time


class Quote(moduletemplate.BotModule):

    def on_module_load(self):
        self.db_file = os.path.join(self.db_dir, "{}_quote.db".format(self.network_name))

        self.register_command("quote", "[Quote ID / Quote String]",
                              "Show a random quote, the quote by ID [Quote ID], or a quote containing [Quote String]",
                              self.PRIV_NONE, ["randomquote"])
        self.register_command("quotedel", "<Quote ID>",
                              "Delete quote by <Quote ID>, you can only delete your own quotes.",
                              self.PRIV_NONE, ["delquote"])
        self.register_command("quoteadd", "<quote>", "Adds <quote> to database.", self.PRIV_NONE, ["addquote"])
        self.register_command("quoteedit", "<Quote ID> <new quote>",
                              "Edit <Quote ID> with <new quote>, you may only edit your own quotes.",
                              self.PRIV_NONE, ["editquote"])
        self.register_command("quotecount", "[account name / host address]",
                              "List total number of quotes in the database.",
                              self.PRIV_NONE, ["countquote", "countquotes"])

        if "quote_ratelimit" not in self.module_data:
            self.module_data["quote_ratelimit"] = 15

        if "quote_ratelimit_individual" not in self.module_data:
            self.module_data["quote_ratelimit_individual"] = True

        self.quote_data = {}

        self.quote_make_db()

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "quote" or command == "randomquote":
            if not self.quote_usable(target, nick):
                return self.notice(nick, "This command is rate-limited, please wait before using it again.")

            if commandtext:
                return self.message(target, nick, self.quote_search(commandtext))
            else:
                return self.message(target, nick, self.quote_random())
        if command == "quoteadd" or command == "addquote":
            if not commandtext:
                return self.notice(nick, "Usage: quoteadd <quote>")

            author = self.get_author(nick)
            if not author:
                return self.notice(nick, "Unable to retrieve account name or hostmask.")

            response = self.quote_add(author, commandtext)
            return self.message(target, nick, response)

        if command == "quoteedit" or command == "editquote":
            ct = commandtext.split()

            if not commandtext or len(ct) < 2 or not ct[0].isdigit():
                return self.notice(nick, "Usage: quoteedit <QuoteID> <modified quote>")

            id = int(ct[0])
            quote = " ".join(ct[1:])

            if not self.quote_exists(id):
                return self.notice(nick, "Quote with ID {} does not exist.".format(id))

            author = self.quote_author(id)
            if author != self.get_author(nick) and not mod:
                return self.notice(nick, "Quote with ID {} was added by {}, you do not have permission to edit it."
                                         .format(id, author))

            failed = self.quote_edit(id, quote)  # will contain a message if it failed, False if it was a success
            if failed:
                return self.message(target, nick, "Failed to edit quote {}: {}".format(id, failed))
            return self.message(target, nick, "Quote {} has been edited.".format(id))

        if command == "quotedel" or command == "delquote":
            if not commandtext or not commandtext.isdigit():
                return self.notice(nick, "Usage: quotedel <QuoteID>")

            id = int(commandtext)
            author = self.quote_author(id)

            if not self.quote_exists(id):
                return self.notice(nick, "Quote with ID {} does not exist.".format(id))

            if author != self.get_author(nick) and not mod:
                return self.notice(nick, "Quote with ID {} was added by {}, you do not have permission to delete "
                                         "it.".format(id, author))

            failure = self.quote_delete(id)
            if failure:
                return self.message(target, nick, "Failed to delete quote {}: {}".format(id, failure))
            return self.message(target, nick, "Successfully deleted quote ID {}.".format(id))

        if command == "quotecount" or command == "countquote" or command == "countquotes":
            if commandtext:
                if commandtext.isalpha() or "@" in commandtext:
                    count = self.quote_count(commandtext)
                    return self.message(target, nick, "There are $(bold){}$(bold) quote{} in my database for "
                                                      "$(bold){}$(bold)."
                                                      .format(count, "s" if count != 1 else "", commandtext), True)
            count = self.quote_count("*")
            return self.message(target, nick, "There are $(bold){}$(bold) quote{} in my database."
                                              .format(count, "s" if count != 1 else ""), True)
        return False

    def get_author(self, nick):
        """Retrieve what is stored as quote author."""
        udata = self.getUserData(nick)
        if udata:
            if udata["account"] and udata["account"] != "0":
                return udata["account"]
            else:
                return "{}@{}".format(udata["user"], udata["host"])
        else:
            return False

    def quote_usable(self, target, nick):
        """Check if channel or nickname can use quote_show again"""
        nick = nick.lower()
        indiv = self.module_data["quote_ratelimit_individual"]

        targ = None  # Indivdual: Ratelimit by nickname, else: ratelimit by target (channel/pm)
        if indiv:
            targ = nick
        else:
            targ = target

        if targ in self.quote_data:
            if int(time.time()) > self.quote_data[targ] + self.module_data["quote_ratelimit"]:
                self.quote_data[targ] = int(time.time())
                return True
            return False
        self.quote_data[targ] = int(time.time())
        return True

    def quote_exists(self, id):
        exists = False
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            result = c.execute("SELECT id FROM quote WHERE id = ?", [id]).fetchone()

            if result and len(result) >= 1:
                exists = True
            conn.close()
        except sqlite3.Error as e:
            self.error("quote_exists({}) error: {}".format(id, str(e)))
            return False
        return exists

    def quote_add(self, author, quote):
        id = 0
        unix_timestamp = int(time.time())
        timestamp = time.strftime("%d %b, %Y")
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            c.execute("INSERT INTO quote (author, quote, timestamp, unix_timestamp) VALUES (?, ?, ?, ?)",
                      [author, quote, timestamp, unix_timestamp])
            id = c.lastrowid

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.error("quote_add({}, {}) error: {}".format(author, quote, str(e)))
            return "Could not add quote: {}".format(str(e))
        return "Quote has been added under the ID {}.".format(id)

    def quote_edit(self, id, newquote):
        """Note: This method returns FALSE on success. An error message on failure."""
        if not self.quote_exists(id):
            return "Quote does not exist."

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            c.execute("UPDATE quote SET quote = ? WHERE id = ? LIMIT 1", [newquote, id])

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.error("quote_edit({}, {}) error: {}".format(id, newquote, str(e)))
            return "Could not edit quote: {}".format(str(e))
        return False  # Returns text (truthy) on failure; false on success.

    def quote_delete(self, id):
        """Note: This method returns FALSE on success. An error message on failure."""
        if not self.quote_exists(id):
            return "Quote does not exist."

        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            c.execute("DELETE FROM quote WHERE id = ? LIMIT 1", [id])

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.error("quote_delete({}) error: {}".format(id, str(e)))
            return "Could not delete quote: {}".format(str(e))
        return False  # Returns text (truthy) on failure; false on success.

    def quote_author(self, id):
        if not self.quote_exists(id):
            return False

        author = ""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            result = c.execute("SELECT author FROM quote WHERE id = ?", [id]).fetchone()

            if result and len(result) >= 1:
                author = result[0]

            conn.close()
        except sqlite3.Error as e:
            self.error("quote_author({}) error: {}".format(author, str(e)))
            return False

        if author:
            return author
        return False

    def quote_random(self):
        quote = ""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            result = c.execute("SELECT id, author, quote, timestamp FROM quote WHERE id >= "
                               "(abs(random()) % (SELECT max(id) FROM quote)) LIMIT 1").fetchone()

            if result:
                quote = "Quote #{} by {}: {} (added on {})".format(result[0], result[1], result[2], result[3])
            else:
                quote = "Could not find a random quote."

            conn.close()
        except sqlite3.Error as e:
            self.error("quote_random() error: {}".format(str(e)))
            return "Could not retrieve random quote: {}".format(str(e))

        if quote:
            return quote
        return "An unknown error occured."

    def quote_search(self, search):
        quote = ""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            if search.isdigit():
                result = c.execute("SELECT id, author, quote, timestamp FROM quote WHERE id = ?",
                                   [search]).fetchone()
            else:
                result = c.execute("SELECT id, author, quote, timestamp FROM quote WHERE lower(quote) LIKE ?",
                                   ["%{}%".format(search.lower())]).fetchone()

            if result and len(result) >= 4:
                quote = "Quote #{} by {}: {} (added on {})".format(result[0], result[1], result[2], result[3])
            else:
                quote = "No such quote was found."

            conn.close()
        except sqlite3.Error as e:
            self.error("quote_search({}) error: {}".format(search, str(e)))
            return "Could not retrieve quote: {}".format(str(e))

        if quote:
            return quote
        return "An unknown error occured."

    def quote_count(self, author):
        count = 0
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = None

            if author == "*":
                result = c.execute("SELECT count(timestamp) FROM quote WHERE 1").fetchone()
            else:
                result = c.execute("SELECT count(timestamp) FROM quote WHERE lower(author) = ?",
                                   [author.lower()]).fetchone()

            if result and len(result) >= 1:
                count = result[0]

            conn.close()
        except sqlite3.Error as e:
            self.error("quote_count({}) error: {}".format(author, str(e)))
            return False
        return count

    def quote_make_db(self):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS quote "
                      "(id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT, author varchar(50), quote TEXT, "
                      "timestamp varchar(20), unix_timestamp INTEGER)")
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.error("quote_make_db() error: {}".format(str(e)))
