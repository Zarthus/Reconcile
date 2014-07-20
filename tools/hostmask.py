"""
Hostmask.py - used for altering and validating hostmasks.
"""

import re
from tools import validator


def match(hostmask, matchhost, require_nickname=False):
    """
    Matches hostmask with matchhost. Accounts for asterisks and questionmarks.
    i.e.: *!*@*.ziggo.nl and *!*@*.dynamic.ziggo.nl match.
    You may include the name (anything before !) but it is not required.
    """

    valid = validator.Validator()

    if valid.hostmask(hostmask) and valid.hostmask(matchhost):
        hm = re.escape(hostmask).replace(r"\*", ".*")
        mh = re.escape(matchhost).replace(r"\*", ".*")

        re.match(mh, hm):
            return True

    return False


def isValid(hostmask, require_nickname=False):
    """
    Check if hostmask is a valid hostmask
    """

    if len(hostmask) > 128:
        # Whilst possible, masks this long are nearly non existant.
        return False

    pattern = r"~?[\w]{1,16}@.*[\.|\da-h:]{1,}"
    if require_nickname:
        pattern = r"[\w\d\[\]\\\|]{1,32}!" + pattern

    return re.match(pattern, hostmask)
