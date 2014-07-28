## Example modules

This is an example module class to be put in the modules/ folder.

By default it has it's module name as `self.module_name` and `self.db_dir` accessable and the following public callbacks:
`on_module_load(self)`, `on_module_unload(self)`, `on_privmsg(self, channel, nick, message)`, `on_action(self, channel, nick, action)`,
`on_command(self, channel, nick, command, commandtext, mod=False, admin=False)`

To respond to users, you can use the methods `reply_channel(channel, nick, message)`, where nick may be None, and it will not preceed the message with the users nickname. 
Be careful your bot does not trigger fantasy commands accidentally if you choose to not use it.  

For a more personal message, you can use `reply_notice(nick, message)` -- sending a notice to the user.  

To get a metadata entry from the config, use `getMetadata("metadata")`

Last is the `requireApiKey("apiname")` to be placed in the on_module_load callback, for a proper example of this please see the class below.  

A module at minimum needs only to extend the BotModule template. Although It won't do anything that way, so you do have to interact with one or more callbacks.
Ideally, untill a more automated system is made, you define `getAvailableCommands(self)` returning a dict of commands available.

Do not forget to check [CONTRIBUTING.md](../CONTRIBUTING.md) to view the guidelines of contributing to this repository.

Without further ado, here is a working example class:

### Example Module

```
"""
ExampleModule by Zarthus
Does things that you expect an Example to do.
"""

from core import moduletemplate


class Example(moduletemplate.BotModule):

    def on_module_load(self):
        # Any exceptions raised within on_module_load will prevent the module from loading,
        # requireApiKey raises an exception, stating the user will need to add an API key for
        # the 'example' in his configuration.
        # If it does not fail, self.api_key["example"] is set to the API key.
        self.requireApiKey("example")
        
        self.register_command("example", "Reply to the user saying this is an example command.", self.PRIV_NONE)
        self.register_command("nexample", "Notice the user saying this is an example command.", self.PRIV_NONE)
        self.register_command("api", "Notice the user with the API key of 'example'", self.PRIV_MOD, ["getapi"])
        
    def on_module_unload(self):
        pass

    def on_privmsg(self, channel, nick, message):
        """
        On privmsg gets sent to the module whenever someone says something to a channel.

        You can handle things like regexes in here, but for general commands you should
        use on_command.
        """
        pass

    def on_action(self, channel, nick, action):
        """See on_privmsg"""
        pass


    def on_command(self, channel, nick, command, commandtext, mod=False, admin=False):
        """
        On command is triggered when someone prefixes the bot by its name, or
        When the command_prefix is sent as first character in a message.

        This means not everything is a command. Modules are to do this on their own.
        In here you could define something like:

        if command == "hello":
            return self.reply_channel(channel, nick, "Hello!")

        The returning of True is important! This means no other modules
        will receive an on_command call, because one has already been processed.

        Return False if no command was processed.
        """

        # Example command, sends a message to the channel.
        if command == "example":
            return self.reply_channel(channel, nick, "This is an example module command")

        # Another example command where instead of messaging the channel, we send a notice to the user.
        if command == "nexample":
            return self.reply_notice(nick, "This is an example module command with a notice")

        # Lastly, a command which checks if the user is an administrator, and then sends the 'example' API
        # key back to the admin.
        if (command == "api" or command == "getapi") and admin:
            return self.reply_notice(nick, "Your API key is: {}".format(self.api_key["example"]))

        return False

```

### Bare module

And here is a bare module containing only the bare essentials:

```
"""
MyModule by Zarthus
Licensed under <license>
<optional contact details>

Module Description.
"""

from core import moduletemplate


class MyModule(moduletemplate.BotModule):

    def on_module_load(self):
        pass

    def on_module_unload(self):
        pass

    def on_privmsg(self, channel, nick, message):
        pass

    def on_action(self, channel, nick, action):
        pass

    def on_command(self, channel, nick, command, commandtext, mod=False, admin=False):
        return False

```

## My module is done, what should I do now?

Check if your module will pass the checks travis will invoke with `python travis/test_module.py modulename` and verify it lives up to the [CONTRIBUTING.md](../CONTRIBUTING.md) standards.  

If it says it's good to go, go ahead and make a pull request.