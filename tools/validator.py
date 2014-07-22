"""
Validator.py:
Helper functions to validate common things in the IRC world, and other things.
"""

import re


class Validator:
    def __init__(self):
        self.valid_username = re.compile(r"~?[\w]{1,16}@")
        self.valid_nickname = re.compile(r"[^ \|`\[\]\\-_\w\d]{1,32}!")

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
