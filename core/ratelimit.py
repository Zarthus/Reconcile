"""
Ratelimiter class by Zarthus,
Put messages in a queue to send them later
"""

from tools import formatter

import threading
import time


class Ratelimit(threading.Thread):
    def __init__(self, conn, logger, burstlimit=4):
        """
        conn: IrcConnection object
        burstlimit: The amount of messages we can send in one go before entering we send our messages slower.
        """

        self._conn = conn
        self.logger = logger

        self.queue_privmsg = []
        self.queue_notice = []
        self.burstlimit = burstlimit
        self.lastburst = time.time()

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
        while self.running:
            itters += 1
            self.getQueues()

            if self.queue_privmsg:
                for message in self.queue_privmsg:
                    self.say(message[0], message[1], message[2])
                    self.queue_privmsg.remove(message)
                    msg_sent = True
                    burstlimit += 1

                    if burstlimit >= self.burstlimit or self.lastburst > time.time() + 5:
                        self.lastburst = time.time()
                        break

            elif self.queue_notice:
                for message in self.queue_notice:
                    self.notice(message[0], message[1], message[2])
                    self.queue_notice.remove(message)
                    msg_sent = True
                    burstlimit += 1

                    if burstlimit >= self.burstlimit or self.lastburst > time.time() + 5:
                        self.lastburst = time.time()
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
        self.queue_privmsg = self.queue_privmsg + self._conn._getPrivmsgQueue()
        self.queue_notice = self.queue_notice + self._conn._getNoticeQueue()

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
