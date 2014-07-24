"""
Basic commands by Zarthus
Licensed under MIT

This is a series of basic commands any bot really should have.
"""

from core import moduletemplate


class BasicCommands(moduletemplate.BotModule):
    """A series of basic commands any bot should have"""

    def on_module_load(self):
        self.register_command("permissions", "Show if you are a bot administrator or moderator", self.PRIV_NONE)
        self.register_command("ping", "Make the bot reply with a message to see if it is still there.", self.PRIV_NONE)
        self.register_command("join", "Join a comma separated list of channels.", self.PRIV_MOD)
        self.register_command("part", "Leave a comma separated list of channels.", self.PRIV_MOD)
        self.register_command("modules", "Display a list of loaded modules.", self.PRIV_MOD)
        self.register_command("shutdown", "Shut the entire bot down. This includes connections to different networks",
                              self.PRIV_ADMIN)

    def on_command(self, channel, nick, command, commandtext, mod=False, admin=False):

        if command == "permissions":
            return self.reply_notice(nick, "Permissions for {}: Administrator: {} - Moderator: {}"
                                           .format(nick, "yes" if admin else "no", "yes" if mod else "no"))

        if command == "ping":
            return self.reply_channel(channel, nick, "Yes, yes. I am here")

        if mod:
            if command == "join":
                if not commandtext:
                    return self.reply_notice(nick, "Usage: join <channels to psart>")

                self._conn.join(commandtext)
                return self.reply_notice(nick, "Attempting to join: {}".format(commandtext.replace(",", ", ")))

            if command == "part":
                if not commandtext:
                    return self.reply_notice(nick, "Usage: part <channels to psart>")

                self._conn.part(commandtext)
                return self.reply_notice(nick, "Attempting to part: {}".format(commandtext.replace(",", ", ")))

            if command == "modules":
                return self.reply_notice(nick, "The following modules are loaded: {}"
                                        .format(str(self._conn.ModuleHandler.getLoadedModulesList())))

            if admin:
                if command == "shutdown":
                    self._conn.quit("Shutdown requested by {}".format(nick))
                    raise KeyboardInterrupt  # TODO: Make a better way to shut the bot down.

        return False
