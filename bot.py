"""
The MIT License (MIT)

Copyright (c) 2014 - 2015 Jos "Zarthus" Ahrens and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

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

try:
    while running:
        time.sleep(1)
        runningThreads = 0
        shutdownRequested = False

        for connection in irc_connections.items():
            running = connection[1].isRunning()
            shutdownRequested = shutdownRequested or connection[1].shutdownRequested
            if running:
                runningThreads += 1

        if runningThreads == 0:
            conf.logger.log("No more connections remain, stopping script.")
            running = False
        if shutdownRequested:
            conf.logger.log("Shutdown requested.")
            for connection in irc_connections.items():
                if connection[1].connected:
                    connection[1].quit("Shutting down...")
                    connection[1].shutdownRequested = False  # to prevent this from running twice.
except KeyboardInterrupt:
    conf.logger.log("Shutdown requested by console.")
    for connection in irc_connections.items():
        if connection[1].connected:
            connection[1].quit("Shutting down...")

os.remove("ircbot.pid")  # Remove pid file as it is no longer running.
