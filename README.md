Reconcile [![Build Status](https://travis-ci.org/Zarthus/Reconcile.svg)](https://travis-ci.org/Zarthus/Reconcile)
=========

A Python Utility bot for python3 and above.  
Compatible with RFC1459 networks such as networks that run charybdis, ircd-seven or ircd-ratbox.  
This bot was designed with Atheme services in mind, and may not work optimally on networks that run different services.

### In development

As of right now, Reconcile is under development and not yet ready for actual use.

## Installation

To make use of Reconcile, ensure the following requirements are met:  

* Running an installation of Windows or Linux (Windows 7, Debian, and Ubuntu are tested)  
* Python 3 or higher is installed (http://python.org)  
* A working internet connection.  
* You have downloaded the requirements with pip or apt-get (`pip install -r requirements.txt`) 
* The network you wish to run this on uses Atheme services. It may not work on other services. 

### Configuring your bot.

Once the installation requirements are satified, copy or rename `config.example.json` to `config.json` and configure it to your liking.  

[Here](https://github.com/Zarthus/Reconcile/wiki/Configuring-Reconcile) is a copy of a configuration with comments -- describing what they do and which options are available.  
But do not copy it directly, use `config.example.json` for that.  

Once these requirements are met, go ahead and run `python bot.py` to start the bot.

### Disabling (or enabling) a module

Modules are automatically loaded if they are in the `modules/` folder, therefore any modules you do not wish to load should be moved to `disabled_modules/`, and vice versa.  

## Contributing  

Should you be willing to contribute to any module, or make your own - it should meet the following guidelines:  

Tested thoroughly,  
Non exploiting - as in that it does not try attempt malicious activities, or otherwise goes against guidelines of tools (such as websites) it is interacting with,  
flake8 ([PEP8](http://legacy.python.org/dev/peps/pep-0008/) and [Pyflakes](https://pypi.python.org/pypi/pyflakes)) compatible,  
Your code is not longer than 119 characters (raised from the original 79 pep8 checks against)  
Travis compatible (see [`.travis.yml`](.travis.yml) to see what tests are being performed)  
[RFC 1459 compatible](http://tools.ietf.org/html/rfc1459.html)
Should your module require an API key, please edit `config.example.json` and `docs/apikeys.md` accordingly.  
Should your module require a configuration block, don't forget to edit the [wiki](https://github.com/Zarthus/Reconcile/wiki/Configuring-Reconcile)

### Bugs / Suggestions
Feel free to make an [issue](https://github.com/zarthus/reconcile/issues/new) if you think you've found a bug, or have a suggestion.

### Support

Should you have issues getting the bot running, have an issue, or have a general inquiry, you can contact me on IRC via [webchat](https://webchat.esper.net/?channels=zarthus) or [connect directly with a client](irc://irc.esper.net/zarthus)  

It may take a while to get a response; and I do not guarantee one, as I am not a 24/7 answering machine. But I'll try my best!
