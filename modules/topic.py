"""
Topic by Zarthus
Licensed under MIT

Fetches the channel topic and returns it to the channel.
"""

from core import moduletemplate


class Topic(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("topic", None, "Get the topic from the channel.", self.PRIV_NONE)
        self.checking_topic = False

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "topic" and target.startswith("#"):
            self.checking_topic = target.lower()
            self.send_raw("TOPIC {}".format(target))
            return True
        return False

    def on_numeric(self, numeric, data):
        # Numeric for topics.
        if numeric == 332:

            if self.checking_topic:
                splitdata = data.split()
                if self.checking_topic == splitdata[3].lower():
                    self.message(self.checking_topic, None, "Topic for {}: {}"
                                                            .format(self.checking_topic,
                                                                    " ".join(splitdata[4:])[1:]))
                    self.checking_topic = False
