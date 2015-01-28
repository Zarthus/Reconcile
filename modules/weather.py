"""
The MIT License (MIT)

Copyright (c) 2014 - 2015 Jos "Zarthus" Ahrens and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Weather by Zarthus
Licensed under MIT

Look up weather data.

Notice: This module may get floody depending on your settings, please ensure you have it properly configured.
If you are unsure what settings are safe, use the default.
"""

from core import moduletemplate
from tools import duration

import requests
import time


class Weather(moduletemplate.BotModule):

    def on_module_load(self):
        self.requireApiKey("weather_underground")

        self.register_command("weather", "<location> [-countrycode]",
                              ("Gather weather information based on <location>. "
                               "The country code should be a 2 letter country code (i.e. US, UK, NL)"),
                              self.PRIV_NONE)

        self.lookups_time = 0
        self.lookups_count = 0
        self.last_lookup = 0
        self.last_lookup_where = None
        self.last_lookup_who = None

        if "use_imperial" not in self.module_data:
            self.module_data["use_imperial"] = False

        if "forecasts_max" not in self.module_data:
            self.module_data["forecasts_max"] = 1

        if self.module_data["forecasts_max"] > 5:
            self.warning("Too high value: Weather forecasts_max is set to {}, "
                         "maximum value: 5. Please edit your configuration and lower this value."
                         .format(self.module_data["forecasts_max"]))
            self.module_data["forecasts_max"] = 5

        if "forecasts_ignore_night" not in self.module_data:
            self.module_data["forecasts_ignore_night"] = False

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if command == "weather":
            if not commandtext:
                return self.notice(nick, "Usage: weather <location> [-countrycode]"
                                         "- country code is US, UK, NL etc.")

            region = ""
            location = commandtext.strip()

            ct = commandtext.split()
            for text in ct:
                if text.startswith("-"):
                    region = text[1:]
                    location = location.replace(text, "").strip().replace(" ", "_")
                    break

            weather = None
            if region and not region.isalpha():
                return self.notice(nick, "Country Code must be alphabetical (i.e. US, UK, NL).")
            if region and location:
                weather = self.check_weather("{}/{}".format(region, location))
            elif location:
                weather = self.check_weather(location)
            else:
                return self.notice(nick, "Could not parse arguments properly. Did you specify a location?")

            if weather:
                if type(weather) == list:
                    for item in weather:
                        # item.startswith($(red)) == colour-parse if it is an alert.
                        # if it doesn't, no need to parse it.
                        self.message(target, nick, item, item.startswith("$(red)"))
                        nick = None  # Set nick to none to prevent multiple highlights.
                else:
                    self.message(target, nick, weather)
            else:
                self.message(target, nick, "Could not find weather information about '{}'".format(commandtext))
            return True
        return False

    def check_weather(self, location):
        """
        Make requests to the API to get the data we need, handling the errors to check if it exists,
        to then process it using parse_weather()
        """
        if self.check_limit():
            return ("This command is limited to 5 lookups per minute, and one lookup every five seconds. "
                    "Please try again later.")

        api_key = self.api_key["weather_underground"]
        api_url = "http://api.wunderground.com/api/{}/alerts/forecast/geolookup/q/{}.json".format(api_key, location)

        json = None
        try:
            r = requests.get(api_url)

            r.raise_for_status()
            json = r.json()
        except Exception as e:
            self.error("Could not find weather information for {}: {}".format(location, str(e)))
            return "Could not find weather information for {}: {}".format(location, str(e))

        contents = ""

        if "response" in json and "results" in json["response"]:
            loc = None

            for res in json["response"]["results"]:
                if "l" in res:
                    loc = res["l"]
                    break

            if not loc:
                return "Could not retrieve location information."

            lookup_url = "http://api.wunderground.com/api/{}/alerts/forecast/geolookup{}.json".format(api_key, loc)
            json = None
            try:
                r = requests.get(lookup_url)

                r.raise_for_status()
                json = r.json()
            except Exception as e:
                self.error("Could not lookup weather information for {}: {}".format(location, str(e)))
                return "Could not lookup weather information for {}: {}".format(location, str(e))

            try:
                # Try to parse the forecast. This normally doesn't trigger any errors
                # but rather safe than sorry, and being descriptive in errors helps.
                # The same happens underneath
                contents = self.parse_weather(json)
            except Exception as e:
                self.error("Error parsing forecast: {}".format(str(e)))
                return "Error parsing forecast: {}".format(str(e))
        elif "forecast" in json:
            try:
                contents = self.parse_weather(json)
            except Exception as e:
                self.error("Error parsing forecast: {}".format(str(e)))
                return "Error parsing forecast: {}".format(str(e))

        if contents:
            return contents

        return "Could not find any results for '{}'.".format(location)

    def parse_weather(self, json):
        """
        So once we actually *have* our result, we want to make a nice (set of) strings from it.
        This function looks in the json that is available and retrieves:
        the forecast, possible alerts, and location data.
        """
        if json and "location" in json and "forecast" in json:
            retlist = []

            fctxt = json["forecast"]["txt_forecast"]

            # Check if it has a state to later append it
            extras = ""
            if "state" in json["location"]:
                if json["location"]["state"]:
                    extras = json["location"]["state"] + ", "

            # Check if there are any alerts
            alerts = False
            if "alerts" in json and len(json["alerts"]):
                alerts = True

            if alerts:
                # If there are alerts, we don't put it on the results line, but give it 1 or 2 separate line(s).

                retlist.append("Results for {}, {}{}, {}.".format(json["location"]["city"],
                                                                  extras, json["location"]["country_name"],
                                                                  json["location"]["country"]))
                # Figure out alert data.
                alerts = json["alerts"][0]
                type = alerts["type"]
                desc = alerts["description"]
                signif = alerts["significance"]

                timedata = ""
                starts = int(alerts["date_epoch"])
                ends = int(alerts["expires_epoch"])

                if int(time.time()) < starts:
                    timedata = ("starts in {}".format(duration.timesincetimestamp(starts)))
                elif int(time.time()) < ends:
                    timedata = ("{} remaining before alert ends".format(duration.timebeforetimestamp(ends)))
                else:
                    timedata = ("ended {} ago".format(duration.timesincetimestamp(ends)))

                message = alerts["message"].replace("\n", " ").replace("  ", " ").strip(" .")

                if len(message) > 50:
                    message = message[:50] + ".."

                retlist.append("$(red){} Type Alert!$(clear) - {} ({}, significance: {}): {}"
                               .format(type, desc, timedata, signif, message))

            else:
                # If there aren't alerts, add it on to the main line.
                retlist.append("Results for {}, {}{}, {} - No weather alerts in the area."
                               .format(json["location"]["city"], extras, json["location"]["country_name"],
                                       json["location"]["country"]))

            itters = 0
            unit_type = "fcttext" if self.module_data["use_imperial"] else "fcttext_metric"
            if "forecastday" in fctxt:
                for fcday in fctxt["forecastday"]:
                    if self.module_data["forecasts_ignore_night"] and fcday["title"].endswith("Night"):
                        continue

                    itters += 1

                    retlist.append("Forecast for {}: {}".format(fcday["title"], fcday[unit_type]))

                    if itters >= self.module_data["forecasts_max"]:
                        break

            if retlist:
                return retlist
            return "No results found"

        if "error" in json["response"]:
            return ("Could not parse forecast (Error: {} - {})"
                    .format(json["response"]["error"]["type"], json["response"]["error"]["description"]))

        return "Could not parse forecast"

    def check_limit(self):
        """
        Check if we can use the command again,

        This checks against:
        Is the time past 60 seconds since the last check? -> Reset calls & time.
        Are we doing more than 5 lookups per minute, or is the last lookup in the past 5 seconds. -> limit crossed.

        Method returns true if we're crossing the limit, false if we are not.
        """
        if int(time.time()) > self.lookups_time + 60:
            self.lookups_time = int(time.time())
            self.lookups_count = 1
        elif self.lookups_count > 5 or int(time.time()) < self.last_lookup + 5:
            return True
        else:
            self.lookups_count += 1

        self.last_lookup = int(time.time())
        return False
