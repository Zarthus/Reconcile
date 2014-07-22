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
        mh = re.escape(matchhost).replace(r"\*", ".*")

        if re.match(mh, hostmask):
            return True

    return False
