"""
Entertainment by Zarthus
Licensed under MIT

Miscellaneous entertainment commands such as coin/slap/hug.
"""

from core import moduletemplate
import random
import time


class Entertainment(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("coin", None, "Flips a coin.", self.PRIV_NONE, ["coinflip"])
        self.register_command("slap", None, "Slap someone.", self.PRIV_NONE)
        self.register_command("pick", "<item1> <item2> [item3 ...]", "Randomly pick one item out of selection.",
                              self.PRIV_NONE)
        self.register_command("hug", None, "Show someone how much you love them!", self.PRIV_NONE)

        self.last_command = {}

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "coin" or command == "coinflip":
            if not self.ratelimit("coin"):  # hardcoded string because of alias.
                return self.reply_notice(nick, "This command is rate limited, please wait before using it again.")

            coinsides = ["heads", "tails"]
            return self.reply_target(target, nick, "The coin lands on $(bold) {} $+ $(clear) ."
                                                   .format(random.choice(coinsides)), True)

        if command == "slap":
            if not self.ratelimit(command):
                return self.reply_notice(nick, "This command is rate limited, please wait before using it again.")

            slapnick = nick if not commandtext else commandtext
            return self.slap(target, slapnick)

        if command == "pick":
            if not commandtext or len(commandtext.split()) < 2:
                return self.reply_notice(nick, "Usage: pick <item1> <item2> [item3 ...]")

            if not self.ratelimit(command):
                return self.reply_notice(nick, "This command is rate limited, please wait before using it again.")

            return self.reply_target(target, nick, random.choice(commandtext.split()))

        if command == "hug":
            if not self.ratelimit(command):
                return self.reply_notice(nick, "This command is rate limited, please wait before using it again.")

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

        return self.reply_action(target, random.choice(slaps).format(slapnick))

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

        return self.reply_action(target, random.choice(hugs).format(hugged))

    def ratelimit(self, command):  # Limit the use of commands - false is recently used, true is can use..
        if ((command not in self.last_command) or
           (command in self.last_command and int(time.time()) > self.last_command[command])):
            self.last_command[command] = int(time.time()) + 10
            return True

        return False
