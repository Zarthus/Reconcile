"""
currency.py by Zarthus
Licensed under MIT

This is a module that introduces commands to convert currencies.
"""

from core import moduletemplate

import requests
import time


class CurrencyConverter(moduletemplate.BotModule):

    def on_module_load(self):
        self.requireApiKey("open_exchange_rates")

        self.register_command("currency", "<amount> <currency> <other currency>",
                              "Convert <amount> <currency> to <other currency>.",
                              self.PRIV_NONE, ["cur", "convert"])
        self.register_command("currencyinfo", "<currency>", "Retrieve informaiton about <currency>.",
                              self.PRIV_NONE, ["curinfo"])

        self.cache = {"convert": {}, "info": {}}
        self.cache_currency_convert()
        self.cache_currency_info()

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
                # Yes, the wikipedia url *may* be invalid, but I trust that most of these do exist.
                return self.reply_target(target, nick, "{} information: Unabbreviated '{}', Wikipedia: {}"
                                                       .format(currency, unabbr, "https://en.wikipedia.org/wiki/{}"
                                                                                 .format(unabbr.replace(" ", "_"))))
            else:
                return self.reply_target(target, nick, "Currency '{}' does not exist or is not known."
                                                       .format(currency))

    def currency_convert(self, amount, currency, ocurrency):
        if time.time() > self.cache["convert"]["age"] + 3600 * 6:
            self.cache_currency_convert()

        if "rates" in self.cache["convert"]["json"]:
            json = self.cache["convert"]["json"]

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
            curInUsd = curInUsd * amount  # Tells us how much USD the amount is worth.
            return curInUsd * ocurrency_one
        return False

    def currency_info(self, currency):
        if time.time() > self.cache["info"]["age"] + 3600 * 6:
            self.cache_currency_info()

        if currency in self.cache["info"]["json"]:
            return self.cache["info"]["json"][currency]
        return False

    def cache_currency_convert(self):
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
            self.logger.notice("Error occured caching currency conversion: {}".format(str(e)))
            return False

        self.cache["convert"]["age"] = time.time()
        self.cache["convert"]["json"] = json
        self.logger.log_verbose("Cached currency conversions.")

        return True

    def cache_currency_info(self):
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
            self.logger.notice("Error occured caching currency info: {}".format(str(e)))
            return False

        self.cache["info"]["age"] = time.time()
        self.cache["info"]["json"] = json
        self.logger.log_verbose("Cached currency information.")
        return True
