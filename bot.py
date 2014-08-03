"""
bot.py: The file that starts it all
Once your bot is configured, running this file will start it up.
"""

from core import config
from core import irc

import time


conf = config.Config()
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
