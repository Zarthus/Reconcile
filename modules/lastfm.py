"""
LastFM.py by Zarthus
Licensed under MIT

Look up recent songs from Last.FM.
"""

from core import moduletemplate
from tools import duration

import requests
import sqlite3
import time
import os


class LastFM(moduletemplate.BotModule):

    def on_module_load(self):
        self.requireApiKey("lastfm")

        self.register_command("lastfm", "[username]", "Look up last.fm data of [username] or yourself if set.",
                              self.PRIV_NONE, ["lfm", "np"])
        self.register_command("lastfmset", "[username]",
                              "Sets your last.fm username to [username]. No parameters means it will be unset",
                              self.PRIV_NONE, ["setlastfm"])
        self.register_command("lastfmunset", None, "Unsets your last.fm username", self.PRIV_NONE, ["unsetlastfm"])
        self.register_command("lastfmget", "<nick>", "Gets <nick>'s set last.fm name.", self.PRIV_MOD, ["getlastfm"])
        self.register_command("lastfmdel", "<nick>", "Deletes <nick>'s set last.fm name.", self.PRIV_MOD,
                              ["dellastfm"])

        self.db_file = os.path.join(self.db_dir, "lastfm.db")
        self.lastfm_create_db()

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "lastfm" or command == "lfm" or command == "np":
            if not commandtext:
                lfmacct = None

                lfmnick = self.lastfm_get_nick(nick)

                if lfmnick:
                    lfmacct = self.lastfm_get_account(lfmnick)
                    if not lfmacct:
                        lfmacct = lfmnick

                if not lfmacct:
                    return self.notice(nick, "Could not find a nick to look up. Please use lastfm <lastfm nick> "
                                             "instead, or set a lastfm account with setlastfm <account name>.")

                return self.lastfm_nowplaying(target, nick, lfmacct)
            else:
                if commandtext.isalnum():
                    return self.lastfm_nowplaying(target, nick, commandtext)
                else:
                    return self.message(target, nick, "Please specify a valid last.fm account name.")

        if command == "unsetlastfm" or command == "lastfmunset":
            lfmnick = self.lastfm_get_nick(nick)

            if not lfmnick:
                return self.notice(nick, "Cannot retrieve nick.")

            if not self.lastfm_get_info(lfmnick):
                return self.message(target, nick, "You do not have a last.fm account bound to you.")

            success = self.lastfm_unset_account(lfmnick)
            if success:
                return self.message(target, nick, "Your last.fm account name has been unset")
            else:
                return self.message(target, nick, "I was unable to delete your data from my database.")

        if command == "setlastfm" or command == "lastfmset":
            if commandtext and not commandtext.isalnum():
                return self.notice(nick, "Usage: setlastfm <username> (must be alphanumeric)")

            lfmnick = self.lastfm_get_nick(nick)
            if not lfmnick:
                return self.notice(nick, "Cannot retrieve nick.")

            if not commandtext:
                if not self.lastfm_get_info(lfmnick):
                    return self.message(target, nick, "You do not have a last.fm account bound to you.")

                success = self.lastfm_unset_account(lfmnick)
                if success:
                    return self.message(target, nick, "Your last.fm account name has been unset")
                else:
                    return self.message(target, nick, "I was unable to delete your data from my database.")
            else:
                success = self.lastfm_set_account(lfmnick, commandtext)
                if success:
                    return self.message(target, nick, "Your last.fm account of '{}' has been bound to {}."
                                                      .format(commandtext, lfmnick))
                else:
                    return self.message(target, nick, "I was unable to store your data in my database.")

        if mod:
            if command == "dellastfm" or command == "lastfmdel":
                if not commandtext or not commandtext.isalnum():
                    return self.notice(nick, "Usage: dellastfm <nick>")

                if not self.lastfm_get_info(commandtext):
                    return self.message(target, nick, "That account does not exist.")

                success = self.lastfm_unset_account(commandtext)
                if success:
                    return self.message(target, nick, "Successfully deleted {}'s last.fm record."
                                                      .format(commandtext))
                else:
                    return self.message(target, nick, "Failed to delete {}'s last.fm record.".format(commandtext))

            if command == "getlastfm" or command == "lastfmget":
                if not commandtext or not commandtext.isalnum():
                    return self.notice(nick, "Usage: getlastfm <nick>")

                data = self.lastfm_get_info(commandtext)
                if data and len(data) == 3:
                    return self.message(target, nick, "{} has their last.fm account set to '{}', set on {}."
                                                      .format(data[0], data[1], data[2]))
                else:
                    return self.message(target, nick, "'{}' does not have a last.fm account bound to their nick."
                                                      .format(commandtext))

        return False

    def lastfm_nowplaying(self, target, nick, account):
        api_url = "http://ws.audioscrobbler.com/2.0/?format=json"
        api_key = self.api_key["lastfm"]

        payload = {
            "format": "json",
            "user": account,
            "api_key": api_key,
            "method": "user.getrecenttracks",
            "limit": 1
        }

        json = ""
        try:
            r = requests.get(api_url, params=payload)
            r.raise_for_status()
            json = r.json
        except Exception as e:
            self.logger.notice("Could not retrieve LastFM np information for {}: {}".format(account, str(e)))
            self.message(target, nick, "Could not retrieve information: {}".format(str(e)))

        acct = ""
        lfmstr = ""

        if "message" in json:
            return self.message(target, nick, json["message"])

        if "@attr" in json:
            acct = json["@attr"]["user"]
        else:
            acct = account

        if "recenttracks" in json and "track" in json["recenttracks"]:
            if not len(json["recenttracks"]["track"]):
                return self.message(target, nick, "{} has not listened to any tracks recently.".format(acct))

            json = json["recenttracks"]["track"]

            if type(json) == dict:  # Not currently playing.
                artist = json["artist"]["#text"]
                song = json["name"]

                album = json["album"]["#text"]
                if album != song and album != artist:
                    album = "from the album ' $+ $(bold) {} $+ $(bold) '".format(album)
                else:
                    album = ""

                timeago = duration.timesincetimestamp(int(json["date"]["uts"]))

                lfmstr = ("$(bold) {} $(bold) last listened to ' $+ $(bold) {} $+ $(bold) ' by "
                          "' $+ $(bold) {} $+ $(bold) ' {} ({} ago)"
                          .format(acct, song, artist, album, timeago)).rstrip() + "."
            elif type(json) == list:  # Currently playing
                json = json[0]

                artist = json["artist"]["#text"]
                song = json["name"]

                album = json["album"]["#text"]
                if album and album != song and album != artist:
                    album = "from the album ' $+ $(bold) {} $+ $(bold) '".format(album)
                else:
                    album = ""

                lfmstr = ("$(bold) {} $(bold) is listening to ' $+ $(bold) {} $+ $(bold) ' by "
                          "' $+ $(bold) {} $+ $(bold) ' {}"
                          .format(acct, song, artist, album)).rstrip() + "."
            else:
                lfmstr = "Could not determine {}'s last played song.".format(acct)

        if lfmstr:
            return self.message(target, nick, lfmstr, True)
        else:
            return self.message(target, nick, "Unable to fetch last.fm information from {}.".format(acct))

    def lastfm_get_nick(self, nick):
        if nick.isalnum():
            return nick

        account = self.getUserData(nick)
        if account:
            if not account["identified"] or account["account"] == "0" or not account["account"].isalnum():
                self.notice(nick, "For security reasons, your name or NickServ account must be alphanumeric.")
                return False
            else:
                return account["account"]
        self.notice(nick, "Your name is not alphanumeric, and I was unable to retrieve your account name.")
        return False

    def lastfm_get_info(self, nick):
        if not nick.isalnum():
            self.logger.notice("lastfm: Possible injection: INSERT for nick '{}' requested.".format(nick))
            return False

        nick = nick.lower()
        data = None
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = c.execute("SELECT nick, account, timestamp FROM lastfm WHERE nick = ?", [nick]).fetchone()

            if result:
                data = result

            conn.close()
        except sqlite3.Error as e:
            self.logger.error("lastfm_get_info({}) error: {}".format(nick, str(e)))
            return False

        return data

    def lastfm_unset_account(self, nick):
        if not nick.isalnum():
            self.logger.notice("lastfm: Possible injection: INSERT for nick '{}' requested.".format(nick))
            return False

        nick = nick.lower()
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("DELETE FROM lastfm WHERE nick = ?", [nick])

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error("lastfm_unset_account({}) error: {}".format(nick, str(e)))
            return False

        return True

    def lastfm_set_account(self, nick, account):
        if not nick.isalnum():
            self.logger.notice("lastfm: Possible injection: INSERT for nick '{}' requested.".format(nick))
            return False
        if not account.isalnum():
            self.logger.notice("lastfm: Possible injection: INSERT for account '{}' requested.".format(account))
            return False

        nick = nick.lower()
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO lastfm (nick, account, timestamp) VALUES (?, ?, ?)", [nick, account, ts])

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error("lastfm_set_account({}, {}) error: {}".format(nick, account, str(e)))
            return False

        return True

    def lastfm_get_account(self, nick):
        if not nick.isalnum():
            self.logger.notice("lastfm: Possible injection: Lookup for '{}' requested.".format(nick))
            return False

        nick = nick.lower()
        account = None
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            result = c.execute("SELECT account FROM lastfm WHERE nick = ?", [nick]).fetchone()

            if result:
                account = result[0]

            conn.close()
        except sqlite3.Error as e:
            self.logger.error("lastfm_get_account({}) error: {}".format(nick, str(e)))
            return False

        return account

    def lastfm_create_db(self):
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS lastfm "
                      "(nick TEXT UNIQUE PRIMARY KEY, account TEXT, timestamp TEXT)")
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error("lastfm_create_db() error: Failed to create database lastfm.db: {}".format(str(e)))
