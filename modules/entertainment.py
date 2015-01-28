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

Entertainment by Zarthus
Licensed under MIT

Miscellaneous entertainment commands such as coin/slap/hug.
"""

from core import moduletemplate
import random


class Entertainment(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("coin", None, "Flips a coin.", self.PRIV_NONE, ["coinflip"])
        self.register_command("slap", None, "Slap someone.", self.PRIV_NONE)
        self.register_command("pick", "<item1> <item2> [item3 ...]", "Randomly pick one item out of selection.",
                              self.PRIV_NONE, ["choose"])
        self.register_command("hug", None, "Show someone how much you love them!", self.PRIV_NONE)

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "coin" or command == "coinflip":
            if not self.ratelimit("coin"):  # hardcoded string because of alias.
                return self.notice(nick, "This command is rate limited, please wait before using it again.")

            coinsides = ["heads", "tails"]
            return self.message(target, nick, "The coin lands on $(bold){}$(clear)."
                                              .format(random.choice(coinsides)), True)

        if command == "slap":
            if not self.ratelimit(command):
                return self.notice(nick, "This command is rate limited, please wait before using it again.")

            slapnick = nick if not commandtext else commandtext
            return self.slap(target, slapnick)

        if command == "pick" or command == "choose":
            if not commandtext or len(commandtext.split()) < 2:
                return self.notice(nick, "Usage: pick <item1> <item2> [item3 ...]")

            if not self.ratelimit(command):
                return self.notice(nick, "This command is rate limited, please wait before using it again.")

            return self.message(target, nick, random.choice(commandtext.split()))

        if command == "hug":
            if not self.ratelimit(command):
                return self.notice(nick, "This command is rate limited, please wait before using it again.")

            return self.hug(target, "everyone" if not commandtext else commandtext)

    def slap(self, target, slapnick):
        slaps = [
            "slaps {} around a bit with a large trout",
            "slaps {} around a bit with a large fishbot",
            "slaps {} around a bit with a large stick",
            "slaps {} around a bit with a small stick",
            "blows leaves in {}'s face using a leafblower",
            "stabs {}",
            "smacks {}",
            "smacks {} onto their head"
        ]

        return self.action(target, random.choice(slaps).format(slapnick))

    def hug(self, target, hugged):
        hugs = [
            "hugs {}",
            "hugs {} with a great passion!",
            "huggles {}",
            "cuddles {}",
            "cuddles with {}",
            "loves {}",
            "comfortingly hugs {}",
            "squeezes {}",
            "gives a big hug to {}",
            "gives {} a virtual love hug"
        ]

        return self.action(target, random.choice(hugs).format(hugged))
