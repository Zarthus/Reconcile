#!/bin/bash
cd $(dirname $0)
rm ircbot.pid
exec /usr/bin/python3 bot.py
