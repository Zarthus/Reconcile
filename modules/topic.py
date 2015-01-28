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
