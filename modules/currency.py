"""
currency.py by Zarthus
Licensed under MIT

This is a module that introduces commands to convert currencies.
"""

from core import moduletemplate

import requests


class CurrencyConverter(moduletemplate.BotModule):

    def on_module_load(self):
        self.requireApiKey("open_exchange_rates")

        self.register_command("currency", "<amount> <currency> <other currency>",
                              "Convert <amount> <currency> to <other currency>.",
                              self.PRIV_NONE, ["cur", "convert"])
        self.register_command("currencyinfo", "<currency>", "Retrieve informaiton about <currency>.",
                              self.PRIV_NONE, ["curinfo"])

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "currency" or command == "cur" or command == "convert":
            if not commandtext or len(commandtext.split()) != 3:
                return self.reply_notice(nick, "Usage: currency <amount> <currency> <other currency>")

            split = commandtext.split()
            amount = split[0]
            currency = split[1].upper()
            ocurrency = split[2].upper()

            if not amount.isdigit():
                return self.reply_notice(nick, "<amount> needs to be a numeric value.")
            if not currency.isalpha():
                return self.reply_notice(nick, "<currency> may only be alphabetic letters.")
            if not ocurrency.isalpha():
                return self.reply_notice(nick, "<other currency> may only be alphabetic letters.")
            if ocurrency == currency:
                return self.reply_notice(nick, "<currency> and <other currency> may not be the same.")

            oamount = self.currency_convert(int(amount), currency, ocurrency)
            if oamount and type(oamount) == float or type(oamount) == int:
                return self.reply_target(target, nick, "$(bold) {} {} $(clear) is equal to $(bold) {} {} $+ $(clear) ."
                                                       .format(amount, currency, round(oamount, 3), ocurrency), True)
            elif oamount:
                return self.reply_target(target, nick, "An error occured: {}".format(oamount))
            else:
                return self.reply_target(target, nick, "Was unable to convert {}{} to {}."
                                                       .format(amount, currency, ocurrency))

        if command == "currencyinfo" or command == "curinfo":
            if not commandtext:
                return self.reply_notice(nick, "Usage: currencyinfo <currency>")

            currency = commandtext.upper()
            unabbr = self.currency_info(currency)
            if unabbr:
                return self.reply_target(target, nick, "{} information: Unabbreviated '{}', Wikipedia: {}"
                                                       .format(currency, unabbr, "https://en.wikipedia.org/wiki/{}"
                                                                                 .format(unabbr.replace(" ", "_"))))
            else:
                return self.reply_target(target, nick, "Currency '{}' does not exist or is not known."
                                                       .format(currency))

    def currency_convert(self, amount, currency, ocurrency):  # TODO: Caching.
        api_url = "http://openexchangerates.org/api/latest.json"
        api_key = self.api_key["open_exchange_rates"]

        payload = {
            "app_id": api_key
        }

        json = None
        try:
            r = requests.get(api_url, params=payload)
            r.raise_for_status()
            json = r.json
        except Exception as e:
            return str(e)

        if "rates" in json:
            # One of <currency>'s worth (in json["base"] -- default USD)
            currency_one = 0
            ocurrency_one = 0

            if currency in json["rates"]:
                currency_one = json["rates"][currency]
            if ocurrency in json["rates"]:
                ocurrency_one = json["rates"][ocurrency]

            if currency_one == 0:
                return "Currency '{}' was not found.".format(currency)
            if ocurrency_one == 0:
                return "Currency '{}' was not found.".format(ocurrency)

            curInUsd = currency_one ** -1  # 1 currency in USD
            print(curInUsd, type(curInUsd), type(amount))
            curInUsd = curInUsd * amount  # Tells us how much USD the amount is worth.

            return curInUsd * ocurrency_one
        return False

    def currency_info(self, currency):
        api_url = "http://openexchangerates.org/api/currencies.json"
        api_key = self.api_key["open_exchange_rates"]

        payload = {
            "app_id": api_key
        }

        json = None
        try:
            r = requests.get(api_url, params=payload)
            r.raise_for_status()
            json = r.json
        except Exception as e:
            return str(e)

        if currency in json:
            return json[currency]
        return False
