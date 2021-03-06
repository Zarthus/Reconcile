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

ChannelManager.py
Manage which channels to join for each network.
"""

import sqlite3
import os


class ChannelManager:
    def __init__(self, db_dir, logger, network_name=None, validator=None):
        self.logger = logger

        if not validator:
            try:
                from tools import validator
                self.validator = validator.Validator()
            except ImportError as e:
                self.logger.error("Failed to import Validator class: {}".format(str(e)))
            except Exception as e:
                self.logger.error("Failed to create Validator class: {}".format(str(e)))
        else:
            self.validator = validator

        self.db_dir = db_dir
        self.network_name = network_name

        if self.network_name:
            self.makeNetworkDB()

    def getList(self):
        return self.getListFromNetwork(self.network_name)

    def getListFromNetwork(self, network_name):
        channels = []

        try:
            conn = sqlite3.connect(self.formatDBFileName(network_name))
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS channels (channel TEXT UNIQUE PRIMARY KEY)")
            result = c.execute("SELECT * FROM channels")

            for row in result.fetchall():
                channels.append(row[0])

            conn.close()
        except sqlite3.Error as e:
            self.logger.error("Failed to retrieve channels for {}:\n{}".format(network_name, str(e)))

        return channels

    def add(self, channel):
        self.addForNetwork(self.network_name, channel)

    def addForNetwork(self, network_name, channel):
        if not self.validator.channel(channel):
            raise Exception("Could not add channel '{}' to {}.db as it doesn't appear to be a channel."
                            .format(channel, network_name))

        try:
            conn = sqlite3.connect(self.formatDBFileName(network_name))
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS channels (channel TEXT UNIQUE PRIMARY KEY)")
            c.execute("INSERT OR REPLACE INTO channels (channel) VALUES (?)", [channel]).rowcount
            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            self.logger.error("Failed to insert channel '{}' to {}.db: {}".format(channel, network_name, str(e)))
        self.logger.log_verbose("Added channel {} to {}.db".format(channel, network_name))

    def delete(self, channel):
        self.delForNetwork(self.network_name, channel)

    def delForNetwork(self, network_name, channel):
        if not self.validator.channel(channel):
            raise Exception("Could not delete channel '{}' from {}.db as it doesn't appear to be a channel."
                            .format(channel, network_name))

        try:
            conn = sqlite3.connect(self.formatDBFileName(network_name))
            c = conn.cursor()
            c.execute("DELETE FROM channels WHERE channel = ?", [channel]).rowcount
            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            self.logger.error("Failed to delete channel '{}' from {}.db: {}".format(channel, network_name, str(e)))
        self.logger.log_verbose("Deleted channel {} from {}.db".format(channel, network_name))

    def makeNetworkDB(self):
        if not self.network_name:
            self.logger.error("Channel Manager: Cannot create Network Database if no network name is specified.")
            return False

        try:
            conn = sqlite3.connect(self.formatDBFileName(self.network_name))
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS channels (channel TEXT UNIQUE PRIMARY KEY)")
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.logger.error("Failed to create channel database {}.db: {}".format(self.network_name, str(e)))

    def formatDBFileName(self, db_name):
        return os.path.join(self.db_dir, "{}_{}.db".format(db_name, db_name))
