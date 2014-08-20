"""
W3 Validator by Zarthus
Licensed under MIT

Validate webpages using W3's validation tool.
"""

from core import moduletemplate

import requests


class W3Validate(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("w3validate", "<website>",
                              "Check if a website is using valid HTML using validator.w3.org",
                              self.PRIV_NONE, ["validate", "val"])
        self.checking_topic = False

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "w3validate" or command == "validate" or command == "val":
            if not commandtext:
                return self.notice(nick, "Usage: w3validate <website>")
            self.message(target, nick, self.w3_validate_url(commandtext), True)
        return False

    def w3_validate_url(self, website):
        val_link = "http://validator.w3.org/check?uri=" + website

        r = None
        try:
            r = requests.get(val_link)
            r.raise_for_status()
        except Exception as e:
            self.logger.notice("Validation for '{}' failed: {}".format(website, str(e)))
            return "Validation for '{}' failed: {}".format(website, str(e))

        valid = r.headers["x-w3c-validator-status"].lower()

        if valid == "valid":
            return "The website {} is $(green){}$(clear). ({})".format(website, valid, val_link)
        if valid == "abort":
            # Possibility that the URL is invalid
            return ("The validation for '{}' $(grey)aborted$(clear) unexpectedly. Is this a valid URL?"
                    .format(website))

        errors = r.headers["x-w3c-validator-errors"]
        warnings = r.headers["x-w3c-validator-warnings"]
        recursion = r.headers["x-w3c-validator-recursion"]

        errstring = ""
        if errors:
            errstring += "Errors: $(red, bold){}$(clear), ".format(errors)
        if warnings:
            errstring += "Warnings: $(orange, bold){}$(clear), ".format(warnings)
        if recursion:
            errstring += "Recursion: $(grey, bold){}$(clear), ".format(recursion)
        if errstring:
            # Remove the ", " from the string.
            errstring = errstring[:-2]
            return "The website {} is $(red){}$(clear). {} ({})".format(website, valid, errstring, val_link)

        return "The website {} is $(red){}$(clear). ({})".format(website, valid, val_link)
