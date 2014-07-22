"""
colours.py:
Pretty colours, colours everywhere
Parses colours using a $(colour) or $(formatting) template.

Supports both the American and British spellings of many colours and words.
"""


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
    "gray": "15"
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

    def getColour(self, colour, return_formatted=True):
        """
        Return numeric in string format of human readable colour formatting.
        Set return_formatted to False to get just the numeric.

        Throws KeyError if colour is not found.
        """

        if colour.lower() not in IRC_COLOUR_DICT:
            raise KeyError("The colour '{}' is not in the list of available colours.".format(colour))

        if return_formatted:
            return self.getFormat("colour") + IRC_COLOUR_DICT[colour.lower()]
        return IRC_COLOUR_DICT[colour.lower()]

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
        IrcFormatter.parse("The quick $(brown) brown $(clear) fox jumps over the $(bold) lazy dog $(clear)")
        To concatinate, use $+ -- i.e. IrcFormatter.parse("$(red) He $(blue) $+ y there")

        This method will not throw any KeyErrors, but will instead ignore input between $() if it doesn't know what to
        replace it with.
        """

        formatted = ""

        for word in string.split(" "):
            if word == "$+":
                formatted = formatted.rstrip()
                continue

            if word.startswith("$(") and word.endswith(")"):
                formatted += self._replace(word[2:-1])
                continue

            formatted += word + " "

        return formatted

    def strip(self, string):
        """strip: Similiar to parse, only this removes colour codes"""

        stripped = ""

        for word in string.split(" "):
            if word == "$+":
                continue

            if word.startswith("$(") and word.endswith(")"):
                continue

            stripped += word + " "

        return stripped.replace("  ", " ").rstrip()

    def _replace(self, string):
        ret = ""
        count = 1
        split = string.lower().split(",")

        for word in split:
            if word.lower() in IRC_COLOUR_DICT:
                if count % 2 == 0:
                    ret += "," + self.getColour(word, False)
                else:
                    ret += self.getColour(word)

                count += 1
            if word.lower() in IRC_FORMATTING_DICT:
                ret += self.getFormat(word)

        return ret