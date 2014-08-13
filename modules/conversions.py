"""
currency.py by Zarthus
Licensed under MIT

This is a module that introduces commands to convert currencies.
"""

from core import moduletemplate

import requests
import time


class Conversions(moduletemplate.BotModule):

    def on_module_load(self):
        self.requireApiKey("open_exchange_rates")

        self.register_command("currency", "<amount> <currency> <other currency>",
                              "Convert <amount> <currency> to <other currency>.",
                              self.PRIV_NONE, ["cur", "convert"])
        self.register_command("currencyinfo", "<currency>", "Retrieve informaiton about <currency>.",
                              self.PRIV_NONE, ["curinfo"])
        self.register_command("temperature", "<temperature> <c/f/k> <c/f/k>",
                              ("Convert degrees in <1> to degrees in <2> (c = celsius, f = fahrenheit, k = kelvin). "
                               "Some aliases of this command need no second and third parameter."),
                              self.PRIV_NONE, ["temp", "cf", "fc", "ck", "kc", "fk", "kf"])
        self.register_command("weight", "<weight> <kg/lb>",
                              "Convert <weight> to <kg/lb>. Aliases of this command need no second parameter.",
                              self.PRIV_NONE, ["kg", "lb"])
        self.register_command("distance", "<distance> <km/mi>",
                              "Convert <distance> to <km/mi>. Some aliases need no second parameter.",
                              self.PRIV_NONE, ["dist", "km", "m", "mi", "miles"])

        self.cache = {"convert": {}, "info": {}}
        self.cache_currency_convert()
        self.cache_currency_info()

        self.kelvin = ["k", "kelvin"]
        self.fahrenheit = ["f", "fahrenheit"]
        self.celsius = ["c", "celsius", "celcius"]
        self.temp_list = self.kelvin + self.fahrenheit + self.celsius

        self.kg = ["kg", "kilogram", "kilograms"]
        self.lb = ["lb", "lbs", "pound"]
        self.weight_list = self.kg + self.lb

        self.km = ["km", "kilometers", "kilometres"]
        self.mi = ["m", "mi", "miles"]
        self.distance_list = self.km + self.mi

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "currency" or command == "cur" or command == "convert":
            if not commandtext or len(commandtext.split()) != 3:
                return self.notice(nick, "Usage: currency <amount> <currency> <other currency>")

            split = commandtext.split()
            amount = split[0]
            currency = split[1].upper()
            ocurrency = split[2].upper()

            if not amount.isdigit():
                return self.notice(nick, "<amount> needs to be a numeric value.")
            if not currency.isalpha():
                return self.notice(nick, "<currency> may only be alphabetic letters.")
            if not ocurrency.isalpha():
                return self.notice(nick, "<other currency> may only be alphabetic letters.")
            if ocurrency == currency:
                return self.notice(nick, "<currency> and <other currency> may not be the same.")

            oamount = self.currency_convert(int(amount), currency, ocurrency)
            if oamount and type(oamount) == float or type(oamount) == int:
                return self.message(target, nick, "$(bold) {} {} $(clear) is equal to $(bold) {} {} $+ $(clear) ."
                                                       .format(amount, currency, round(oamount, 3), ocurrency), True)
            elif oamount:
                return self.message(target, nick, "An error occured: {}".format(oamount))
            else:
                return self.message(target, nick, "Was unable to convert {}{} to {}."
                                                       .format(amount, currency, ocurrency))

        if command == "currencyinfo" or command == "curinfo":
            if not commandtext:
                return self.notice(nick, "Usage: currencyinfo <currency>")

            currency = commandtext.upper()
            unabbr = self.currency_info(currency)
            if unabbr:
                # Yes, the wikipedia url *may* be invalid, but I trust that most of these do exist.
                return self.message(target, nick, "{} information: Unabbreviated '{}', Wikipedia: {}"
                                                       .format(currency, unabbr, "https://en.wikipedia.org/wiki/{}"
                                                                                 .format(unabbr.replace(" ", "_"))))
            else:
                return self.message(target, nick, "Currency '{}' does not exist or is not known."
                                                       .format(currency))

        if command in ["cf", "fc", "ck", "kc", "fk", "kf"]:  # Aliases for 'temperature'
            commandtext = "{} {} {}".format(commandtext, command[0], command[1])
            command = "temperature"

        if command == "temperature" or command == "temp":
            ct = commandtext.lower().split()

            if not commandtext or len(ct) != 3 or ct[1] not in self.temp_list or ct[2] not in self.temp_list:
                return self.notice(nick, "Syntax: temperature <temperature> <c/f/k> <c/f/k>")
            if not ct[0].replace(".", "").isdigit():
                return self.notice(nick, "Temperature has to be a digit")
            if ct[1] == ct[2]:
                return self.notice(nick, "You cannot convert two of the same temperatures.")

            temp = float(ct[0])
            tempname = ""
            newtemp = 0
            newtempname = ""

            if ct[1] in self.celsius and ct[2] in self.fahrenheit:  # c -> f
                newtemp = temp * 9 / 5 + 32

                tempname = "°C"
                newtempname = "°F"
            elif ct[1] in self.celsius and ct[2] in self.kelvin:  # c -> k
                newtemp = temp + 273.15

                tempname = "°C"
                newtempname = "K"
            elif ct[1] in self.fahrenheit and ct[2] in self.celsius:  # f -> c
                newtemp = (temp - 32) * 5 / 9

                tempname = "°F"
                newtempname = "°C"
            elif ct[1] in self.fahrenheit and ct[2] in self.kelvin:  # f -> k
                newtemp = 5 / 9 * (temp - 32) + 273.15

                tempname = "°F"
                newtempname = "K"
            elif ct[1] in self.kelvin and ct[2] in self.celsius:  # k -> c
                newtemp = temp - 273.15

                tempname = "°C"
                newtempname = "K"
            elif ct[1] in self.kelvin and ct[2] in self.fahrenheit:  # k -> f
                newtemp = 9 / 5 * (temp - 273.15) + 32

                tempname = "K"
                newtempname = "°F"
            else:
                self.logger.notice("Temperature Conversion: Not found in lists: {}".format(commandtext))
                return self.notice(nick, "An error occured: Conversion type was not found.")

            newtemp = round(newtemp, 2)
            tempstring = ("$(bold) {} {} $(clear) is equal to $(bold) {} {}"
                          .format(temp, tempname, newtemp, newtempname))
            return self.message(target, nick, tempstring, True)

        if command in ["kg", "lb"]:  # Aliases for 'weight'
            commandtext = "{} {}".format(commandtext, command)
            command = "weight"

        if command == "weight":
            ct = commandtext.lower().split()

            if not commandtext or len(ct) != 2 or ct[1] not in self.weight_list:
                return self.notice(nick, "Syntax: weight <weight> <kg/lb>")
            if not ct[0].replace(".", "").isdigit():
                return self.notice(nick, "Weight has to be a digit")

            weight = float(ct[0])
            weightname = ""
            newweight = 0
            newweightname = ""

            if ct[1] in self.kg:
                newweight = weight / 2.2046

                weightname = "lb" if int(weight) == 1 else "lbs"
                newweightname = "kg"
            elif ct[1] in self.lb:
                newweight = weight * 2.2046

                weightname = "kg"
                newweightname = "lb" if int(newweight) == 1 else "lbs"
            else:
                self.logger.notice("Weight Conversion: Not found in lists: {}".format(commandtext))
                return self.notice(nick, "An error occured: Conversion type was not found.")

            newweight = round(newweight, 2)
            weightstring = ("$(bold) {} {} $(clear) is equal to $(bold) {} {}"
                            .format(weight, weightname, newweight, newweightname))
            return self.message(target, nick, weightstring, True)

        if command in ["km", "m", "mi"]:
            commandtext = "{} {}".format(commandtext, command)
            command = "distance"

        if command == "distance" or command == "dist":
            ct = commandtext.lower().split()

            if not commandtext or len(ct) != 2 or ct[1] not in self.distance_list:
                return self.notice(nick, "Syntax: distance <distance> <km/mi>")
            if not ct[0].replace(".", "").isdigit():
                return self.notice(nick, "Distance has to be a digit")

            dist = float(ct[0])
            distname = ""
            newdist = 0
            newdistname = ""

            if ct[1] in self.km:
                newdist = dist / 0.62137

                distname = "mile" if int(dist) == 1 else "miles"
                newdistname = "kilometer" if int(newdist) == 1 else "kilometers"
            elif ct[1] in self.mi:
                newdist = dist * 1.60934

                distname = "kilometer" if int(dist) == 1 else "kilometers"
                newdistname = "mile" if int(newdist) == 1 else "miles"
            else:
                self.logger.notice("Distance Conversion: Not found in lists: {}".format(commandtext))
                return self.notice(nick, "An error occured: Conversion type was not found.")

            newdist = round(newdist, 2)
            diststring = ("$(bold) {} {} $(clear) is equal to $(bold) {} {}"
                          .format(dist, distname, newdist, newdistname))
            return self.message(target, nick, diststring, True)

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
