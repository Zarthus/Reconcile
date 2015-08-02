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
"""

import re


class IgnoreList:
    def __init__(self, ignorelist):
        if ignorelist:
            self.ignorelist = ignorelist
        else:
            self.ignorelist = []

    def isIgnored(self, target):
        if target.lower() in self.ignorelist:
            return True

        for user in self.ignorelist:
            if "*" in user:
                userRegex = self.compileIgnore(user)
                if userRegex.match(target):
                    return True

        return False

    def isIgnoredWildcard(self, wctarget):
        if "*" not in wctarget:
            return self.isIgnored(wctarget)

        target = self.compileIgnore(wctarget)

        for user in self.ignorelist:
            if target.match(user):
                return True

            if "*" in user:
                userRegex = self.compileIgnore(user)
                if userRegex.match(wctarget):
                    return True

        return False

    def ignore(self, target):
        if target.lower() in self.ignorelist:
            return False

        self.ignorelist.append(target.lower())
        return True

    def unignore(self, target):
        if target.lower() in self.ignorelist:
            self.ignorelist.remove(target.lower())
            return True

        return False

    def getIgnoreList(self):
        return self.ignorelist

    def compileIgnore(self, target):
        return re.compile(re.escape(target)
                            .replace("\\*", ".*")
                            .replace("\\?", "."), re.I)
