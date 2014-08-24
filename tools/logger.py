"""
Logger class for the bot
"""

import time
import os


class Logger:
    def __init__(self, network_name, logDir=False, verbose=False,
                 timestamp="%H:%M", logTimestamp="%Y-%m-%d %H:%M:%S", useColours=True):
        self.network_name = network_name
        self.logging = True if logDir else False
        self.logDir = logDir
        self.verbose = verbose
        self.timestamp = timestamp
        self.logTimestamp = logTimestamp
        self._setColours(useColours)

    def log(self, text):
        print("{} {} | {}".format(self.getTimestamp(), self.network_name, text))
        self._write("[{}] {}".format(self.getLogTimestamp(), text))

    def notice(self, text):
        print("{}{} {} | Notice: {}{}".format(self.col_notice_prefix, self.getTimestamp(), self.network_name, text,
                                              self.col_notice_suffix))
        self._write("[{}] [NOTICE] {}".format(self.getLogTimestamp(), text))

    def error(self, text):
        print("{}{} {} | Error: {}{}".format(self.col_error_prefix, self.getTimestamp(), self.network_name, text,
                                             self.col_error_suffix))
        self._write("[{}] [ERROR] {}".format(self.getLogTimestamp(), text))

    def event(self, event, text):
        print("{} {} | {} - {}".format(self.getTimestamp(), self.network_name, event, text))
        self._write("[{}] [{}] {}".format(self.getLogTimestamp(), event, text))

    def debug(self, text):
        """
        debug() should be used with care, if you need to log something, use log_verbose, if something went wrong
        that normally shouldn't, use debug()

        in short, if the user should see the message, use debug(), if it's rather irrelevant, use log_verbose
        """

        print("{}{} {} | Debug: {}{}".format(self.col_debug_prefix, self.getTimestamp(), self.network_name, text,
                                             self.col_debug_suffix))
        self._write("[{}] [DEBUG] {}".format(self.getLogTimestamp(), text))

    def log_verbose(self, text):
        if self.verbose:
            print("{} {} | {}".format(self.getTimestamp(), self.network_name, text))
            self._write("[{}] [VERBOSE] {}".format(self.getLogTimestamp(), text))

    def notice_verbose(self, text):
        if self.verbose:
            print("{} {} | Notice: {}".format(self.getTimestamp(), self.network_name, text))
            self._write("[{}] [VERBOSE] [NOTICE] {}".format(self.getLogTimestamp(), text))

    def setVerbose(self, verbose):
        self.verbose = verbose

    def setTimestamp(self, timestamp):
        self.timestamp = timestamp

    def getTimestamp(self):
        return time.strftime(self.timestamp)

    def setLogTimestamp(self, timestamp):
        self.logTimestamp = timestamp

    def getLogTimestamp(self):
        return time.strftime(self.logTimestamp)

    def _setColours(self, useColours=True):
        if useColours:
            if os.name == "posix":
                self.col_notice_prefix = "\033[93m"
                self.col_notice_suffix = "\033[0m"

                self.col_error_prefix = "\033[31m"
                self.col_error_suffix = "\033[0m"

                self.col_debug_prefix = "\033[94m"
                self.col_debug_suffix = "\033[0m"
            else:
                self._setColoursNone()
        else:
            self._setColoursNone()

    def _setColoursNone(self):
        self.col_notice_prefix = ""
        self.col_notice_suffix = ""

        self.col_error_prefix = ""
        self.col_error_suffix = ""

        self.col_debug_prefix = ""
        self.col_debug_suffix = ""

    def _write(self, message, file=None):
        """Log content to disk."""
        if not self.logging:
            return
        if not file:
            file = self.network_name + time.strftime(".%Y-%m-%d") + ".log"
        if not file.endswith(".log"):
            file = file + ".log"

        logfile = os.path.join(self.logDir, file)

        if not os.path.isfile(logfile):
            f = open(logfile, "w")
        else:
            f = open(logfile, "a")

        f.write(message + "\n")
        f.close()
