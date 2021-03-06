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

Ratelimiter class by Zarthus,
Put messages in a queue to send them later
"""

from tools import formatter

import threading
import time


class Ratelimit(threading.Thread):
    def __init__(self, conn, logger, burstlimit=5):
        """
        conn: IrcConnection object
        burstlimit: The amount of messages we can send in one go before entering we send our messages slower.
        """

        self._conn = conn
        self.logger = logger

        self.queue_privmsg = []
        self.queue_notice = []
        self.burstlimit = burstlimit
        self.lastburst = int(time.time())

        self.running = True

        threading.Thread.__init__(self)

    def run(self):
        """
        An infinite loop checking if items are in the queue to process,
        if there are, we enter a for loop iterating over these queued messages, and dispatch them appropriately.
        Should there be an excessive amount of messages (self.burstlimit) we enter a state where messages are
        rate limited to be sent once every second.

        The burst limitation ends after 5 seconds of not sending any messages.
        """

        itters = 0
        burstlimit = 0
        msg_sent = False  # Whenever we don't send a message, we don't need to get into a long sleep.
        self.getQueues()
        while self.running:
            itters += 1

            while not self.queue_privmsg.empty():
                message = self.queue_privmsg.get()

                self.say(message[0], message[1], message[2])
                msg_sent = True
                burstlimit += 1

                if burstlimit >= self.burstlimit or int(time.time()) < self.lastburst:
                    self.lastburst = int(time.time())
                    break

            while not self.queue_notice.empty():
                message = self.queue_notice.get()

                self.notice(message[0], message[1], message[2])
                msg_sent = True
                burstlimit += 1

                if burstlimit >= self.burstlimit or int(time.time()) < self.lastburst + 5:
                    self.lastburst = int(time.time())
                    break

            if msg_sent:
                time.sleep(2)
                msg_sent = False
            else:
                time.sleep(.25)

            if itters % 3 == 0 and burstlimit != 0:
                # Resets the burst limit every 6 seconds.
                itters = 0
                burstlimit = 0

    def stop(self):
        if not self.running:
            self.logger.notice("Cannot stop ratelimiter thread: Not running.")
            return False

        self._conn.logger.log("Stopping ratelimiter thread.")
        self.running = False

    def getQueues(self):
        self.queue_privmsg = self._conn._getPrivmsgQueue()
        self.queue_notice = self._conn._getNoticeQueue()

    def say(self, target, message, format):
        """
        Sends a message to target
        With formatting enabled, we will attempt to parse the contents through the IrcFormatter class.
        """

        if not format:
            self.logger.log("Sending PRIVMSG '{}' to {}.".format(message, target))
            self._conn.send_raw("PRIVMSG {} :{}".format(target, message))
        else:
            parser = formatter.IrcFormatter()
            self.logger.log("Sending parsed PRIVMSG '{}' to {}.".format(message, target))
            self._conn.send_raw("PRIVMSG {} :{}".format(target, parser.parse(message)))

    def notice(self, target, notice, format):
        """
        Sends a NOTICE to target
        With formatting enabled, we will attempt to parse the contents through the IrcFormatter class.
        """

        if not format:
            self.logger.log("Sending NOTICE '{}' to {}.".format(notice, target))
            self._conn.send_raw("NOTICE {} :{}".format(target, notice))
        else:
            parser = formatter.IrcFormatter()
            self.logger.log("Sending parsed NOTICE '{}' to {}.".format(notice, target))
            self._conn.send_raw("NOTICE {} :{}".format(target, parser.parse(notice)))
