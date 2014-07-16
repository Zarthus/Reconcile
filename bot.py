"""
bot.py: The file that starts it all
Once your bot is configured, running this file will start it up.
"""

from tools import hostmask
from core import config
from core import irc

import time


conf = config.Config()
irc_connections = {}
running = True

for network in conf.getNetworks().iteritems():
    irc_connections[network[0]] = irc.IrcConnection(network[1])

while running:
    try: 
        for connection in irc_connections.iteritems():
            connection[1].tick()
    except KeyboardInterrupt:
        print("KeyboardInterrupt caught, bot exiting")
        running = False
    except Exception as e:
        print("Caught Exception:\n{}".format(str(e)))
        
    
    time.sleep(0.1)
