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

Here is a copy of a configuration with comments -- but do not copy it directly, use `config.example.json` for that.   

```
{
  "irc": { // irc block
    "espernet": { // name of the block.
      "server": "irc.esper.net", // server to connect to.
      "port": 6667, // port to connect to - do not use a plus sign.
      "ssl": false, // connecting with ssl or not 

      "nick": "Reconcile", // the primary nickname to try. 
      "altnick": "Reconcile_", // if the primary nickname is taken, we connect with this instead. Leave blank for nick_

      "ident": "reconcile", // the ident (also known as username) of the bot 
      "realname": "Zarthus his bot", // the real name of the bot, if left blank it will contain a link to the github repository

      "account": "zarthus-bots", // the account to identify to.
      "password": "irc-password", // the password the bot should use to identify to the account specified.

      "command_prefix": "!", // The prefix all commands will have.
      "invite_join": true, // join channels when invited by anyone
      
      // This is an OPTIONAL setting. Not specifying means you will make use of storing and deleting channels dynamically.
      // If you only want your bot to be in a specific set of channels and nowhere else. As such, it is not shown in the default config.
      "channels": [
          "#channel1", "#channel2"
      ],

      // A list of administrators, supports wildcard *, nickname (anything before !) can be left out.
      // administrators have access to everything, use this with caution.
      "administrators": [
        "Zarthus!Zarthus@zarth.us"
      ],
      
      "moderators": [
        "hej@hello.me",
        "bye@goodbye.net",
        "*@moderate.us"
      ]
    }
  },

  // a list of api keys some modules require, modules will automatically unload themselves if no api key was found.
  // It is recommended to move modules which you don't have an api key of to modules_disabled.
  "api_keys": {
    "something": "", // Api key for some application
    "somethingelse": "" // Api key for another application.
  },
  
  // bot metadata, generally data that is used in certain modules.
  "metadata": {
    "bot_version": "0.2", // the bot version
    "bot_maintainer": "Zarthus", // the bot maintainer, change this to your own name
    "github_url": "https:\/\/github.com\/zarthus\/reconcile", // a link to the github repository where the source code can be found
    "verbose": true, // verbosity; some things will not be logged if this is set to false. Can be useful for debugging.
    
    "db_dir": "db/", // In which folder do we store database files?
    
    "timestamp": "%H:%M" // strftime format of how a timestamp should look, https://docs.python.org/3/library/time.html#time.strftime
  }
}

```

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

### Bugs / Suggestions
Feel free to make an [issue](https://github.com/zarthus/reconcile/issues/new) if you think you've found a bug, or have a suggestion.

### Support

Should you have issues getting the bot running, have an issue, or have a general inquiry, you can contact me on IRC via [webchat](https://webchat.esper.net/?channels=zarthus) or [connect directly with a client](irc://irc.esper.net/zarthus)  

It may take a while to get a response; and I do not guarantee one, as I am not a 24/7 answering machine. But I'll try my best!
