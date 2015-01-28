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

Validator.py:
Helper functions to validate common things in the IRC world, and other things.
"""

import re


class Validator:
    def __init__(self):
        self.valid_username = re.compile(r"~?[\w]{1,16}@")
        self.valid_nickname = re.compile(r"[\|\`\[\]\\\-\_\w\d]{1,32}!")

    def hostmask(self, hostmask, require_nickname=False):
        """Check if hostmask is a valid hostmask"""

        if len(hostmask) > 128:
            # Whilst possible, masks this long are nearly non existant.
            return False

        hostmask = hostmask.replace(":", "")

        if self.valid_username.search(hostmask):
            if require_nickname:
                return self.valid_nickname.match(hostmask)
            return True

        return False

    def nickname(self, nick):
        """Check if nick is a valid IRC nickname"""
        if self.valid_nickname.match(nick + "!"):
            return True
        return False

    def channel(self, channel):
        """Check if channel is a valid channelname"""
        if channel.startswith("#"):
            return True
        return False
