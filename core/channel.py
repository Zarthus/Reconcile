"""
ChannelManager.py
Manage which channels to join for each network.
"""

import sqlite3


class ChannelManager:
    def __init__(self, db_dir, validator=None):
        if not validator:
            try:
                from tools import validator
                self.validator = validator.Validator()
            except ImportError as e:
                print("Failed to import Validator class: {}".format(str(e)))
            except Exception as e:
                print("Failed to create Validator class: {}".format(str(e)))
        else:
            self.validator = validator

        self.db_dir = db_dir

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
            print("Failed to retrieve channels for {}:\n{}".format(network_name, str(e)))

        return channels

    def addForNetwork(self, network_name, channel):
        if not self.validator.channel(channel):
            raise Exception("Could not add channel '{}' to {}.db as it doesn't appear to be a channel."
                            .format(channel, network_name))

        try:
            conn = sqlite3.connect(self.formatDBFileName(network_name))
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS channels (channel TEXT UNIQUE PRIMARY KEY)")
            c.execute("INSERT OR REPLACE INTO channels (channel) VALUES (?)", [channel])
            conn.commit()
            conn.close()

            print("Added channel {} to {}.db".format(channel, network_name))
        except sqlite3.Error as e:
            print("Failed to insert channel '{}' to {}.db: {}".format(channel, network_name, str(e)))

    def delForNetwork(self, network_name, channel):
        if not self.validator.channel(channel):
            raise Exception("Could not delete channel '{}' from {}.db as it doesn't appear to be a channel."
                            .format(channel, network_name))

        try:
            conn = sqlite3.connect(self.formatDBFileName(network_name))
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS channels (channel TEXT UNIQUE PRIMARY KEY)")
            c.execute("DELETE FROM channels WHERE channel = ?", [channel])
            conn.commit()
            conn.close()
            print("Deleted channel {} from {}.db".format(channel, network_name))
        except sqlite3.Error as e:
            print("Failed to delete channel '{}' from {}.db: {}".format(channel, network_name, str(e)))

    def formatDBFileName(self, db_name):
        return self.db_dir + db_name + ".db"
