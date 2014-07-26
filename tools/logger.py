"""
Logger class for the bot
"""

import time

class Logger:
    def __init__(self, network_name, verbose=False, timestamp="%H:%M"):
        self.network_name = network_name
        self.verbose = verbose
        self.timestamp = timestamp

    def log(self, text):
        print("{} {} | {}".format(self.getTimestamp(), self.network_name, text))

    def notice(self, text):
        print("{} {} | Notice: {}".format(self.getTimestamp(), self.network_name, text))

    def error(self, text):
        print("{} {} | ERROR: {}".format(self.getTimestamp(), self.network_name, text))

    def event(self, event, text):
        print("{} {} | {} - {}".format(self.getTimestamp(), self.network_name, event, text))

    def log_verbose(self, text):
        if self.verbose:
            print("{} {} | {}".format(self.getTimestamp(), self.network_name, text))

    def notice_verbose(self, text):
        if self.verbose:
            print("{} {} | Notice: {}".format(self.getTimestamp(), self.network_name, text))

    def setVerbose(self, verbose):
        self.verbose = verbose

    def setTimestamp(self, timestamp):
        self.timestamp = timestamp

    def getTimestamp(self):
        return time.strftime(self.timestamp)