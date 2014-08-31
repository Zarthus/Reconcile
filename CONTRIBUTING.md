Reconcile - contributing
========================

Should you be willing to contribute to any module, or make your own - it should meet the following guidelines:  

Tested thoroughly,  
Non exploiting - as in that it does not try attempt malicious activities, or otherwise goes against guidelines of tools (such as websites) it is interacting with,  
flake8 ([PEP8](http://legacy.python.org/dev/peps/pep-0008/) and [Pyflakes](https://pypi.python.org/pypi/pyflakes)) compatible,  
Your code is not longer than 119 characters (raised from the original 79 pep8 checks against)  
Travis compatible (see [`.travis.yml`](.travis.yml) to see what tests are being performed)  
[RFC 1459 compatible](http://tools.ietf.org/html/rfc1459.html)  
Should your module require an API key, please edit `config.example.json` and [the Wiki Page](https://github.com/Zarthus/Reconcile/wiki/API-Keys) accordingly (in alphabetical order).
Should your module require a configuration block, don't forget to edit the [wiki](https://github.com/Zarthus/Reconcile/wiki/Configuring-Reconcile)  
Optionally, feel free to add yourself to CONTRIBUTORS.md or ask any maintainer to add you once your Pull Request gets accepted.

### Making The Pull Request

If the requirements are met, feel free to submit in a pull request. It is recommended you work from a different branch that describes what you are changing  
(i.e. if you are changing a module called `tetris.py`, name it something like `tetris-add-square-block`, but is entirely optional).



### Bugs / Suggestions
Feel free to make an [issue](https://github.com/zarthus/reconcile/issues/new) if you think you've found a bug, or have a suggestion.

### Support

If the [Wiki Pages](https://github.com/Zarthus/Reconcile/wiki) are of no help, and you need assistance with a script or have a general inquiry, you can contact me on IRC via [webchat](https://webchat.esper.net/?channels=zarthus) or [connect directly with a client](irc://irc.esper.net/zarthus)  

