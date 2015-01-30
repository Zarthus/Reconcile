Reconcile [![Build Status](https://travis-ci.org/Zarthus/Reconcile.svg)](https://travis-ci.org/Zarthus/Reconcile)
=========

A Python Utility bot for python3 and above.  
Compatible with RFC1459 networks such as networks that run charybdis, ircd-seven or ircd-ratbox.  
This bot was designed with Atheme services in mind, and may not work optimally on networks that run different services.  

## Installation

To make use of Reconcile, ensure the following requirements are met:

* Reconcile is tested and only verified to work on Linux (Debian, Ubuntu), while it *should* run on both Windows and Mac, we do not guarantee full compatibility.
* Python 3 or higher is installed (http://python.org)
* A working internet connection.
* You have downloaded the requirements with pip or apt-get (`pip install -r requirements.txt`)
* To have `screen` installed (for the init script and start.sh).
* Ideally, have a UTF-8 locale configured - encoding problems may occur if this is not the case.

### Configuring your bot.

Once the installation requirements are satified, copy or rename `config.example.json` to `config.json` and configure it to your liking.

[Here](https://github.com/Zarthus/Reconcile/wiki/Configuring-Reconcile) is a copy of a configuration with comments -- describing what they do and which options are available.
But do not copy it directly, use `config.example.json` for that.

Once these requirements are met, go ahead and run `python bot.py` or `./start.sh` to start the bot.

### Run the bot on system init.

To run the bot on init you can copy (as root or via sudo) the file `reconcile` (from the root of the repo) to /etc/init.d/  
You will then want to edit the file (do this as root/via sudo!).  
Change the BOTUSER and BOTDIR variables to match your setup.  
Make sure to chmod +x the init script in /etc/init.d/  
Make sure to have `screen` installed!  

### Disabling (or enabling) a module

Modules are automatically loaded if they are in the `modules/` folder, therefore any modules you do not wish to load should be moved to `modules_disabled/`, and vice versa.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) if you would like to contribute to the Reconcile project.  

### Bugs / Suggestions
Feel free to make an [issue](https://github.com/zarthus/reconcile/issues/new) if you think you've found a bug, or have a suggestion.

### Support

If the [Wiki Pages](https://github.com/Zarthus/Reconcile/wiki) are of no help, and still have an issue, or have a general inquiry, you can contact me on IRC via [webchat](https://webchat.esper.net/?channels=zarthus) or [connect directly with a client](irc://irc.esper.net/zarthus)

It may take a while to get a response; and I do not guarantee one, as I am not a 24/7 answering machine. But I'll try my best!
