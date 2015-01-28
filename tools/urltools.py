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

UrlTools: Interact and manipulate URLs
"""

import bs4
import urllib.request

from tools import shorturl
from tools import urlparse


class UrlTools:
    SHORTEN_SERVICES = ["isgd", "googl", "scenesat"]

    def isUrl(url):
        return urlparse.Url(url).isUrl()

    def shorten(url, service, api_key=None, logger=None, ret_false=False):
        if service not in UrlTools.SHORTEN_SERVICES:
            return False if ret_false else "Service was not in available services."

        if not UrlTools.isUrl(url):
            return False if ret_false else "Url provided was not an URL."

        if api_key and service in api_key:
            api_key = api_key[service]
        else:
            api_key = None

        return getattr(shorturl.ShortUrl, service)(url=url, api_key=api_key, logger=logger)

    def getAvailableServices():
        serv = ""

        for s in UrlTools.SHORTEN_SERVICES:
            serv += s + ", "

        return serv[:-2]

    def getDefaultShortenService():
        return UrlTools.SHORTEN_SERVICES[0]

    def getTitle(url, ret_false=False):
        if not UrlTools.isUrl(url):
            return None

        try:
            soup = bs4.BeautifulSoup(urllib.request.urlopen(url))
        except Exception as e:
            return "Failed to parse '{}' with error '{}'".format(url, str(e)) if not ret_false else False

        if not soup or not soup.title or not soup.title.string:
            return "Failed to parse '{}'".format(url) if not ret_false else False

        title = soup.title.string
        if not len(title):
            return "Cannot find title for '{}'".format(url) if not ret_false else False

        return title.strip()
