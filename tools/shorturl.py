"""
shorturl.py by Zarthus,
Licensed under MIT
"""

import requests
import json


class ShortUrl:
    """
    shorturl.py: Serveral methods to simplify URLs.

    All methods in this class are 'static' and support the 'logger' parameter,
    Whenever possible, passing this parameter ensures errors will be logged to console, so it is recommended you do.
    """

    def isgd(url, logger=None):
        """
        Shorten an URL with http://is.gd

        url: string, url to shorten

        returns shortened url, or False on failure.
        Information: http://is.gd/apishorteningreference.php
        """

        isgd = "http://is.gd/create.php"
        payload = {
            "format": "json",
            "url": url
        }

        shorturl = ""

        try:
            r = requests.get(isgd, params=payload)

            if r.ok and "shorturl" in r.json:
                shorturl = r.json["shorturl"]
            else:
                r.raise_for_status()
        except Exception as e:
            if logger:
                logger.error("Failed to shorten '{}': {}".format(url, str(e)))

        if shorturl:
            return shorturl
        return False

    def scenesat(url, apikey=None, alias=None, password=None, logger=None):
        """
        Shorten an URL with http://scenes.at

        url: string, url to shorten
        apikey: string, Your API key
        alias: string, Alias for the URL to have.
        password: string, Password the shorturl should have to be accessed.

        returns shortened url, or False on failure.
        Information: http://scenes.at/i/api
        """

        scenesat = "http://scenes.at/c"
        payload = {
            "link": url,
            "api": "yes",
            "key": apikey
        }

        if alias:
            payload["alias"] = alias
        if password:
            payload["pwd"] = password

        shorturl = ""

        try:
            r = requests.get(scenesat, params=payload)

            if r.ok and "shorturl" in r.json:
                shorturl = r.json["shorturl"]
            else:
                r.raise_for_status()
        except Exception as e:
            if logger:
                logger.error("Failed to shorten '{}': {}".format(url, str(e)))

        if shorturl:
            return shorturl
        return False
