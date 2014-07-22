class BotModule:

    def __init__(self, conn, module_name):
        self._conn = conn
        self.module_name = module_name
        self.db_dir = self._conn.config.getDatabaseDir()

    def on_module_load(self):
        """Module constructor"""
        pass

    def on_module_unload(self):
        """Module destructor"""
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

        return False

    def reply_channel(self, channel, nick, message):
        """
        Reply to the user by sending a message to the channel,
        Use this for comamnds that contain non-sensitive data that completed successfully.

        Not specifying 'nick' means the command will be sent without addressing the user,
        it may be useful in some situations, but generally is not recommended.
        """

        if nick:
            message = "{}: {}".format(nick, message)

        self._conn.say(channel, message)

        return True

    def reply_notice(self, nick, message):
        """
        Reply to the user with a notice,
        Use this for errors, syntax information or sending private data.
        """

        self._conn.notice(nick, message)

        return True

    def getAvailableCommands(self):
        """
        If you want your command listed as help entry, here is where we do it.

        Return a dict following syntax:
        {
            "commandname": {
                "priv": "none",
                "help": "command help desc"
            },
            "command2": {
                "priv": "mod",
                "help": "do something good"
            }
        }

        Supported privileges: none, mod, moderator, admin, administrator
        Do not include the command prefix.

        You don't need to include every command, although it is advised you do.
        """

        return {}

    def requireApiKey(api_name):
        """
        If your module requires an API key, call this method in on_module_load to instruct the user to add an API
        key to his configuration if it doesn't exist.

        We will let the Module Handler catch the error, and thus the module will not be loaded.
        """
        if not self._getApiKey(api_name):
            raise Exception("Module {} requires API key '{}', but none was provided. Please edit your configuration to"
                            " include an API key.".format(self.module_name, api_name))

        self.api_key[api_name] = self._getApiKey(api_name)

    def _getApiKey(api_name):
        return self._conn.config.getApiKey(api_name)
    
    def getConfigMetadata(metadata):
        return self._conn.config.getMetadata(metadata)
    
