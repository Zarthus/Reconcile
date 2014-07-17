"""
bot.py: The file that starts it all
Once your bot is configured, running this file will start it up.
"""

from core import config
from core import irc

import time
import sys


conf = config.Config()
irc_connections = {}
running = True

for network in conf.getNetworks().iteritems():
    irc_connections[network[0]] = irc.IrcConnection(network[1], conf)

while running:
    time.sleep(0.1)

    try:
        for connection in irc_connections.iteritems():
            connection[1].tick()
    except KeyboardInterrupt:
        print("KeyboardInterrupt caught, bot exiting")

        for c in irc_connections.iteritems():
            c[1].quit("Shutdown requested by Console")
        running = False
    except Exception as e:
        print("Caught Exception:\n{}".format(str(e)))
        print(sys.exc_info())
