"""
bot.py: The file that starts it all
Once your bot is configured, running this file will start it up.
"""

from core import config
from core import irc

import time
import os


conf = config.Config()

if os.path.isfile("ircbot.pid"):  # There is a pid file, the bot is already running. Stop.
    conf.logger.error("An ircbot.pid file exists, there is already an instance of the bot running.")
    conf.logger.error("Please shut down that instance of the bot and run this command again.")
    import sys
    sys.exit(1)

f = open("ircbot.pid", "w")
f.write(str(os.getpid()))
f.close()

irc_connections = {}
running = True

for network in conf.getNetworks().items():
    irc_connections[network[0]] = irc.IrcConnection(network[1], conf)

while running:
    time.sleep(0.1)

    for connection in irc_connections.items():
        force_quit = connection[1].tick()
        if force_quit:
            print("Quit requested, bot exiting")

            for c in irc_connections.items():
                c[1].quit("Shutdown requested.")
            running = False

os.remove("ircbot.pid")  # Remove pid file as it is no longer running.