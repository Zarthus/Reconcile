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

    def googl(url, api_key=None, logger=None):
        """
        Shorten an URL with http://goo.gl - googles own url shortener.

        url: string, url to shorten
        api_key: api key

        returns shortened url, or False on failure
        Information: https://developers.google.com/url-shortener/v1/getting_started
        """

        url = "https://www.googleapis.com/urlshortener/v1/url"
        payload = {
            "longUrl": url
        }
        if api_key:
            payload["key"] = api_key

        header = {
            "Content-Type": "application/json"
        }

        shorturl = ""
        try:
            r = requests.post(url, data=json.dumps(payload), headers=header)

            if r.ok and "id" in r.json():
                shorturl = r.json()["id"]
            else:
                r.raise_for_status()
        except Exception as e:
            if logger:
                logger.error("goo.gl: Failed to shorten '{}': {}".format(url, str(e)))

        if shorturl:
            return shorturl
        return False

    def isgd(url, api_key=None, logger=None):
        """
        Shorten an URL with http://is.gd

        url: string, url to shorten
        api_key: None, is not used

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

            if r.ok and "shorturl" in r.json():
                shorturl = r.json()["shorturl"]
            else:
                r.raise_for_status()
        except Exception as e:
            if logger:
                logger.error("is.gd: Failed to shorten '{}': {}".format(url, str(e)))

        if shorturl:
            return shorturl
        return False

    def scenesat(url, api_key=None, alias=None, password=None, logger=None):
        """
        Shorten an URL with http://scenes.at

        url: string, url to shorten
        api_key: string, Your API key
        alias: string, Alias for the URL to have.
        password: string, Password the shorturl should have to be accessed.

        returns shortened url, or False on failure.
        Information: http://scenes.at/i/api
        """

        scenesat = "http://scenes.at/c"
        payload = {
            "link": url,
            "api": "yes",
            "key": api_key
        }

        if alias:
            payload["alias"] = alias
        if password:
            payload["pwd"] = password

        shorturl = ""

        try:
            r = requests.get(scenesat, params=payload)

            if r.ok and "shorturl" in r.json():
                shorturl = r.json()["shorturl"]
            else:
                r.raise_for_status()
        except Exception as e:
            if logger:
                logger.error("scenes.at: Failed to shorten '{}': {}".format(url, str(e)))

        if shorturl:
            return shorturl
        return False
