"""
bot.py: The file that starts it all
Once your bot is configured, running this file will start it up.
"""

from core import config
from core import irc

import time
import traceback
import sys

print("Reconcile Python Bot -- Running Python {}.{}".format(sys.version_info[0], sys.version_info[1]))

conf = config.Config()
irc_connections = {}
running = True

for network in conf.getNetworks().items():
    irc_connections[network[0]] = irc.IrcConnection(network[1], conf)

while running:
    time.sleep(0.1)

    try:
        for connection in irc_connections.items():
            connection[1].tick()
    except KeyboardInterrupt:
        print("KeyboardInterrupt caught, bot exiting")

        for c in irc_connections.items():
            c[1].quit("Shutdown requested by Console")
        running = False
    except Exception as e:
        traceback.print_exc()
