"""
Logger class for the bot
"""


class Logger:
    def __init__(self, network_name, verbose=False):
        self.network_name = network_name
        self.verbose = verbose

    def log(self, text):
        print("{} | {}".format(self.network_name, text))

    def notice(self, text):
        print("{} | Notice: {}".format(self.network_name, text))

    def error(self, text):
        print("{} | ERROR: {}".format(self.network_name, text))

    def event(self, event, text):
        print("{} | {} - {}".format(self.network_name, event, text))

    def log_verbose(self, text):
        if self.verbose:
            print("{} | {}".format(self.network_name, text))

    def notice_verbose(self, text):
        if self.verbose:
            print("{} | Notice: {}".format(self.network_name, text))

    def setVerbose(self, verbose):
        self.verbose = verbose
