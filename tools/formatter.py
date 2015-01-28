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

colours.py:
Pretty colours, colours everywhere
Parses colours using a $(colour) or $(formatting) template.

Supports both the American and British spellings of many colours and words.
"""

import re
from random import randint


IRC_COLOUR_DICT = {
    "white": "00",
    "black": "01",
    "dblue": "02",
    "dark_blue": "02",
    "dark_green": "03",
    "dgreen": "03",
    "red": "04",
    "dark_red": "05",
    "dred": "05",
    "brown": "05",  # Note: This appears to show up as brown for some clients, dark red for others.
    "purple": "06",
    "orange": "07",
    "yellow": "08",
    "green": "09",
    "lime": "09",
    "cyan": "10",
    "teal": "11",
    "blue": "12",
    "pink": "13",
    "dgrey": "14",
    "dark_grey": "14",
    "dgray": "14",
    "dark_gray": "14",
    "grey": "15",
    "gray": "15",
    "random": ""  # Special keyword, generate a random number.
}

IRC_FORMATTING_DICT = {
    "colour": "\x03",
    "color": "\x03",

    "bold": "\x02",
    "b": "\x02",

    "underlined": "\x1F",
    "underline": "\x1F",
    "ul": "\x1F",

    "italics": "\x1D",
    "italic": "\x1D",
    "i": "\x1D",

    "reverse": "\x16",

    "reset": "\x0F",
    "clear": "\x0F"
}


class IrcFormatter:
    """A class which manipulates strings to fit in colours - supports both American and British spellings"""

    def __init__(self):
        self.getColor = self.getColour
        self.getAvailableColors = self.getAvailableColours

        self.colour_re = re.compile(r"\$\(.*?\)", re.I)

    def getColour(self, colour, return_formatted=True):
        """
        Return numeric in string format of human readable colour formatting.
        Set return_formatted to False to get just the numeric.

        Throws KeyError if colour is not found.
        """
        colour = colour.lower()

        if colour not in IRC_COLOUR_DICT:
            raise KeyError("The colour '{}' is not in the list of available colours.".format(colour))

        if colour == "random":  # Special keyword for a random colour
            rand = randint(0, 15)
            if rand < 10:  # Prepend '0' before colour so it always is double digits.
                rand = "0" + str(rand)
            rand = str(rand)

            if return_formatted:
                return self.getFormat("colour") + rand
            return rand

        if return_formatted:
            return self.getFormat("colour") + IRC_COLOUR_DICT[colour]
        return IRC_COLOUR_DICT[colour]

    def getFormat(self, formatting):
        """
        Return hex-character in string format of human readable formatting.

        Throws KeyError if formatting is not found.
        """

        if formatting.lower() not in IRC_FORMATTING_DICT:
            raise KeyError("The formatting '{}' is not found in the list of available formats.".format(formatting))

        return IRC_FORMATTING_DICT[formatting.lower()]

    def getAvailableFormats(self):
        """List the formats you can use in self.getFormat in a comma separated list (string)"""

        ret = ""
        for formats in IRC_FORMATTING_DICT:
            ret += formats + ", "

        return ret[:-2]

    def getAvailableColours(self):
        """List the colours you can use in self.getColour in a comma separated list (string)"""

        ret = ""
        for colours in IRC_COLOUR_DICT:
            ret += colours + ", "

        return ret[:-2]

    def parse(self, string):
        """
        parse: Formats a string, replacing words wrapped in $( ) with actual colours or formatting.

        example:
        IrcFormatter.parse("The quick $(brown)brown$(clear) fox jumps over the$(bold) lazy dog$(clear).")

        This method will not throw any KeyErrors, but will instead ignore input between $() if it doesn't know what to
        replace it with.
        """

        formatted = string
        regex = self.colour_re.findall(string)
        for match in regex:
            formatted = formatted.replace(match, self._convert(match), 1)

        return formatted

    def strip(self, string):
        """strip: Similiar to parse, only this removes colour codes"""

        stripped = ""

        regex = self.colour_re.split(string)
        for match in regex:
            stripped += match

        return stripped.strip()

    def _convert(self, string):
        if not string.startswith("$(") and not string.endswith(")"):
            return string
        string = string[2:-1]
        ret = ""
        count = 1
        formattings = string.lower().replace(" ", "").split(",")
        for formatting in formattings:
            if formatting in IRC_COLOUR_DICT:
                if count % 2 == 0:
                    ret += "," + self.getColour(formatting, False)
                else:
                    ret += self.getColour(formatting)
                count += 1
            elif formatting in IRC_FORMATTING_DICT:
                ret += self.getFormat(formatting)

        return ret.strip()
