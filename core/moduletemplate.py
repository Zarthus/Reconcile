class BotModule:

    PRIV_NONE = "none"
    PRIV_MOD = "mod"
    PRIV_MODERATOR = "mod"
    PRIV_ADMIN = "admin"
    PRIV_ADMINISTRATOR = "admin"

    def __init__(self, conn, logger, module_name):
        self._conn = conn
        self.logger = logger
        self.module_name = module_name
        self.db_dir = self._conn.config.getDatabaseDir()

        self._registered_commands = []
        self.api_key = {}
        self.module_data = self._getModuleData()

        self.isBotAdmin = self.isBotAdministrator  # aliases for admin/moderator
        self.isBotMod = self.isBotModerator

    def on_module_load(self):
        """Module constructor"""
        pass

    def on_module_unload(self):
        """Module destructor"""
        pass

    def on_privmsg(self, target, nick, message):
        """
        On privmsg gets sent to the module whenever someone says something to a target.

        You can handle things like regexes in here, but for general commands you should
        use on_command.
        """
        pass

    def on_action(self, target, nick, action):
        """See on_privmsg"""
        pass

    def on_command(self, target, nick, command, commandtext, mod, admin):
        """
        On command is triggered when someone prefixes the bot by its name, or
        When the command_prefix is sent as first character in a message.

        This means not everything is a command. Modules are to do this on their own.
        In here you could define something like:

        if command == "hello":
            return self.reply_target(target, nick, "Hello!")

        The returning of True is important! This means no other modules
        will receive an on_command call, because one has already been processed.

        Return False if no command was processed.
        """
        return False

    def on_numeric(self, numeric, data):
        """
        Whenever the server sends a numeric reply thos callback gets called.

        numeric: integer, numeric sent by the server.
        data: string, anything after the numeric. What varies per numeric.
        """
        pass

    def reply_target(self, target, nick, message, parse=False):
        """
        Reply to the user by sending a message to the channel or user,
        Use this for comamnds that contain non-sensitive data that completed successfully.

        Not specifying 'nick' means the command will be sent without addressing the user,
        it may be useful in some situations, but generally is not recommended.

        You should always use a channel as target unless the command was performed in a private message.
        """

        if nick and target.startswith("#"):
            message = "{}: {}".format(nick, message)

        self._conn.say(target, message, parse)

        return True

    def reply_notice(self, nick, message, parse=False):
        """
        Reply to the user with a notice,
        Use this for errors, syntax information or sending private data.
        """

        self._conn.notice(nick, message, parse)

        return True

    def reply_action(self, target, action, parse=False):
        """
        Reply to the user or channel with an ACTION,
        Useful for general fun commands or when the bot needs to 'do' something.

        ACTIONs are not rate limited, and should be used with care.
        """

        self._conn.action(target, action, parse)

        return True

    def send_raw(self, raw_message):
        """
        Send a raw message to the network.

        Please use this sparingly, and make sure it complies with the RFC.
        """

        self.logger.log("Module '{}' sending raw message: '{}'".format(self.module_name, raw_message))
        self._conn.send_raw(raw_message)

    def isOp(self, nick, channel):
        return self._conn.isOp(nick, channel)

    def isVoice(self, nick, channel):
        return self._conn.isVoice(nick, channel)

    def isOn(self, nick, channel):
        return self._conn.isOn(nick, channel)

    def isIdentified(self, nick):
        return self._conn.isIdentified(nick)

    def isOper(self, nick):
        return self._conn.isOper(nick)

    def getUserData(self, nick):
        return self._conn.getUserData(nick)

    def getChannelData(self, channel):
        return self._conn.getChannelData(channel)

    def isBotAdministrator(self, nick):
        return self._conn.isBotAdmin(nick)

    def isBotModerator(self, nick):
        return self._conn.isBotModerator(nick)

    def register_command(self, command, params, help, priv, aliases=None):
        """
        Register a command to the bots core help module.

        command: string, name of the command
        help: string, help description
        priv: string, either self.PRIV_NONE, self.PRIV_MOD, or self.PRIV_ADMIN
        aliases: list, list of strings containing aliases of this command.
        """

        self._conn.register_command(command, params, help, priv, aliases, self.module_name)
        self._registered_commands.append(command)

    def unregister_command(self, command):
        if command in self._registered_commands:
            self._registered_commands = self._registered_commands.pop(command)
            self._conn.unregister_command(command)

            return True
        return False

    def getConfigMetadata(self, metadata):
        return self._conn.config.getMetadata(metadata)

    def requireApiKey(self, api_name):
        """
        If your module requires an API key, call this method in on_module_load to instruct the user to add an API
        key to his configuration if it doesn't exist.

        We will let the Module Handler catch the error, and thus the module will not be loaded.
        """
        if not self._getApiKey(api_name):
            raise Exception("Module {} requires API key '{}', but none was provided. Please edit your configuration to"
                            " include an API key.".format(self.module_name, api_name))

        self.api_key[api_name] = self._getApiKey(api_name)

    def _getApiKey(self, api_name):
        return self._conn.config.getApiKey(api_name)

    def _unregister_commands(self):
        for cmd in self._registered_commands:
            self._conn.unregister_command(cmd)

    def _getModuleData(self):
        """Read the config's module block for an entry matching the class name of the module."""
        mdata = self._conn.config.getModuleData(self.module_name)
        if mdata:
            return mdata
        else:
            return []