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
