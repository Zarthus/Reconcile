"""
Logger class for the bot
"""

import time
import os


class Logger:
    def __init__(self, network_name, verbose=False, timestamp="%H:%M", useColours=True):
        self.network_name = network_name
        self.verbose = verbose
        self.timestamp = timestamp
        self.setColours(useColours)

    def log(self, text):
        print("{} {} | {}".format(self.getTimestamp(), self.network_name, text))

    def notice(self, text):
        print("{}{} {} | Notice: {}{}".format(self.col_notice_prefix, self.getTimestamp(), self.network_name, text,
                                              self.col_notice_suffix))

    def error(self, text):
        print("{}{} {} | Error: {}{}".format(self.col_error_prefix, self.getTimestamp(), self.network_name, text,
                                             self.col_error_suffix))

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

    def setColours(self, useColours=True):
        if useColours:
            if os.name == "posix":
                self.col_notice_prefix = "\033[93m"
                self.col_notice_suffix = "\033[0m"

                self.col_error_prefix = "\033[31m"
                self.col_error_suffix = "\033[0m"
            else:
                self.setColoursNone()
        else:
            self.setColoursNone()

    def setColoursNone(self):
        self.col_notice_prefix = ""
        self.col_notice_suffix = ""

        self.col_error_prefix = ""
        self.col_error_suffix = ""
