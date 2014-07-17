"""
Validator.py:
Helper functions to validate common things in the IRC world, and other things.
"""

import re


class Validator:

    def hostmask(hostmask, require_nickanme=False):
        """Check if hostmask is a valid hostmask"""

        if len(hostmask) > 128:
            # Whilst possible, masks this long are nearly non existant.
            return False

        pattern = r"~?[\w]{1,16}@.*[\.|\da-h:]{1,}"
        if require_nickname:
            pattern = r"[\w\d\[\]\\\|]{1,32}!" + pattern

        return re.match(pattern, hostmask)

    def nickname(nick):
        """Check if nick is a valid IRC nickname"""
        if re.match(r"[^ \|`\[\]\\-_\w\d]", nick):
            return False
        return True

    def channel(channel):
        """Check if channel is a valid channelname"""
        if channel.startswith("#"):
            return True
        return False
