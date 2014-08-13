"""
FloodDebug by Zarthus
Licensed under MIT

This module will flood, allowing you to debug the rate limitation system.
"""

from core import moduletemplate

import time


class FloodDebug(moduletemplate.BotModule):
    def on_module_load(self):
        self.register_command("flood_notice", None, "Flood your notice with ten messages.", self.PRIV_ADMIN)
        self.register_command("flood_channel", None, "Flood the channel with ten messages.", self.PRIV_ADMIN)
        self.register_command("flood_query", None, "Flood your query with ten messages.", self.PRIV_ADMIN)

        self.last_flood = int(time.time())

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if admin:
            if command == "flood_notice":
                if int(time.time()) > self.last_flood + 5:
                    self.last_flood = int(time.time())
                    for i in range(10):
                        self.notice(nick, "flood_notice(): Message {}".format(i))

                    return True

            if command == "flood_channel":
                if int(time.time()) > self.last_flood + 5:
                    self.last_flood = int(time.time())
                    for i in range(10):
                        self.message(target, nick, "flood_channel(): Message {}".format(i))

                    return True

            if command == "flood_query":
                if int(time.time()) > self.last_flood + 5:
                    self.last_flood = int(time.time())
                    for i in range(10):
                        self.message(nick, None, "flood_query(): Message {}".format(i))

                    return True
