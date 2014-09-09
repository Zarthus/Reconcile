"""
bot.py: The file that starts it all
Once your bot is configured, running this file will start it up.
"""

import sys


if sys.version_info.major < 3:  # We will fail to import core if we're not on python 3, check this first.
    print("Error: You require python 3 or higher, currently on python {}.{}"
          .format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)


from core import config
from core import irc

import time
import os


conf = config.Config()

try:
    if os.getuid() == 0 or os.geteuid() == 0:
        conf.logger.error("You may not run this script as root.")
        sys.exit(1)
except AttributeError:
    pass

if os.path.isfile("ircbot.pid"):  # There is a pid file, the bot is already running. Stop.
    conf.logger.error("An ircbot.pid file exists, there is already an instance of the bot running.")
    conf.logger.error("Please shut down that instance of the bot and run this command again.")
    sys.exit(1)

f = open("ircbot.pid", "w")
f.write(str(os.getpid()))
f.close()

irc_connections = {}
running = True

for network in conf.getNetworks().items():
    irc_connections[network[0]] = irc.IrcConnection(network[1], conf)

while running:
    time.sleep(1)
    runningThreads = 0

    for connection in irc_connections.items():
        running = connection[1].isRunning()

        if running:
            runningThreads += 1

    if runningThreads == 0:
        conf.logger.log("No more connections remain, stopping script.")
        running = False

os.remove("ircbot.pid")  # Remove pid file as it is no longer running.
