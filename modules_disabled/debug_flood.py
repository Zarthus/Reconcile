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
        return False
