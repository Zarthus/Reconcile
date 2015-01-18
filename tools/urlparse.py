"""
Url.py, a tool for accurate URL detection and slight manipulation.

To use, import the class, and call either Url.find(string), Url.findAll(string), or Url(url)
More accurate documentation is available on the Wiki, https://github.com/Zarthus/Reconcile/wiki/Tools:-Url.py
"""

import re
import urllib.parse


# These series of regexes are meant to work together. Alone they might lead to mismatches.
# The entire regex looks like this: (?:(\w+?)(?::\/\/))?([\w\.]+)\.([a-z]{2,16})(?::(\+?[1-9]\d{1,4}))?(\/[^ ]+)?
RE_PROTOCOL = r"(?:([\w\-_]+?)(?::\/\/))?"  # (1) match the protocol, strip :// e.g. https or ssh
RE_DOMAIN = r"([\w\-_\.]+)"  # (2) match the domain, and any subdomains. e.g. www.google, google, or maps.google
RE_TLD = r"\.([a-z]{2,16})"  # (3) The top level domain, does not account for unicode. e.g. com, info, org
RE_PORT = r"(?::(\+?[1-9]\d{1,4}))?"  # (4) The port. e.g. google.com:100 extracts 100
RE_PATH = r"(\/[^ ]+)?"  # (5) Get everything after the top level domain / port starting with a slash. e.g. /hi.html
URL_REGEX = re.compile(RE_PROTOCOL + RE_DOMAIN + RE_TLD + RE_PORT + RE_PATH, re.I)


class Url:
    """The URL class, determine how likely a string is a URL by performing a series of checks on it."""

    CERTAINTY_CAP = 100

    def __init__(self, url, min_certainty=50):
        self.min_certainty = Url.CERTAINTY_CAP if min_certainty > Url.CERTAINTY_CAP else min_certainty
        self.certainty = 0

        self.encoded = None
        self.decoded = None

        self.url = url

        self.protocol = None
        self.subdomains = []
        self.domain = None
        self.tld = None
        self.port = None
        self.path = None

        self.factors = []

        self._parse()
        self._calculateCertainty()

    def getCertainty(self):
        """"Returns an integer, the certainty that the URL has attained based on certain factors"""
        return self.certainty

    def getMinCertainty(self):
        """Returns an integer, the minimum amount of certainty required before this is detected as a valid URL"""
        return self.min_certainty

    def getUrl(self):
        """Return the URL specified when the class was created, string"""
        return self.url

    def getProtocol(self):
        """Return the protocol used, or None"""
        return self.protocol

    def getSubdomains(self):
        """Return a list of subdomains or an empty list"""
        return self.subdomains

    def getDomain(self):
        """Return the domain, or None"""
        return self.domain

    def getPort(self):
        """Return the port, or None"""
        if self.port:
            return self.port

        port_map = {
            "ftp": 21,
            "ssh": 22,
            "telnet": 23,
            "http": 80,
            "https": 443,
            "irc": 6667,
            "ircs": 6697
        }

        if self.protocol and self.protocol in port_map:
            self.port = port_map[self.protocol]

        return self.port

    def getTld(self):
        """Return the top level domain or None"""
        return self.tld

    def getPath(self):
        """Return a string of the path (anything past the top level domain / port) or None"""
        return self.path

    def getFactors(self):
        """Return a list of factors that this url matches that affected the URL certainty"""
        return self.factors

    def getAsDict(self):
        return {
            "url": self.url,
            "certainty": self.certainty,
            "min_certainty": self.min_certainty,
            "factors": self.factors,

            "protocol": self.protocol,
            "subdomains": self.subdomains,
            "domain": self.domain,
            "tld": self.tld,
            "port": self.getPort(),
            "path": self.path,

            "encoded": self.encode(),
            "decoded": self.decode()
        }

    def find(string):
        """
        Find an URL in a string

        Returns an Url Object if URL an was found, or None
        """
        match = URL_REGEX.search(string)

        if match:
            return Url(string[match.start():match.end()])
        return None

    def findAll(string):
        """
        find all urls in a string.

        Returns a list of Url Objects, or an empty list if no urls are found
        """
        matches = URL_REGEX.finditer(string)

        urls = []

        if matches:
            for match in matches:
                url = string[match.start():match.end()]
                urls.append(Url(url))

        return urls

    def isUrl(self):
        """Return a boolean value if the specified URL is considered a valid URL or not."""
        return self.certainty >= self.min_certainty

    def encode(self):
        """Encode an URL"""
        if self.encoded:
            return self.encoded

        if self.path:
            self.encoded = self.url.replace(self.path, urllib.parse.quote(self.path))
        else:
            self.encoded = self.url

        return self.encoded

    def decode(self):
        """Decode an URL"""
        if self.decoded:
            return self.decoded

        self.decoded = urllib.parse.unquote(self.url)
        return self.decoded

    def _parse(self):
        """Parse an URL, filling all variables with their respective values."""
        match = URL_REGEX.match(self.url)

        if not match:
            self._addCertainty(-50, "Does not match URL regex")
            return

        groups = match.groups()

        subdom = groups[1].split('.')
        dom = subdom[len(subdom) - 1] if len(subdom) != 0 else None

        if dom:
            subdom.remove(dom)

        self.protocol = groups[0]
        self.subdomains = subdom
        self.domain = dom
        self.tld = groups[2]
        self.port = groups[3]
        self.path = groups[4]

    def _calculateCertainty(self):
        """
        Calculate how certain we are that something is an URL.
        In general the URL regex will match valid URLs, but it becomes less accurate the less context is provided.

        There are valid URLs like google.com, this attempts to calculate how likely the specified string is an URL
        based on a large amount of factors stored in getFactors()
        """

        if self.protocol:
            if self.protocol in ["http", "https"]:
                self._addCertainty(30, "Use of " + self.protocol + " protocol")
            elif self.protocol in ["ftp", "ssh", "telnet", "irc", "ircs"]:
                self._addCertainty(20, "Use of " + self.protocol + " protocol")

        if self.subdomains:
            subdomain_count = 0
            for subdomain in self.subdomains:
                subdomain_count += 1

                if subdomain_count > 3:
                    self._addCertainty(-30, "More than three subdomains found [" + str(len(self.subdomains)) + "], " +
                                            " more than realistically likely.")
                    break

                if subdomain == 'www':
                    self._addCertainty(20, "Subdomain found: '" + subdomain + "'")
                else:
                    self._addCertainty(10, "Subdomain found: '" + subdomain + "'")

        if not self.domain:
            self._addCertainty(-50, "No primary domain name found.")
        else:
            if self.domain.isalpha():
                self._addCertainty(20, "Primary domain is alphabetical.")
            elif self.domain.replace('-', '').isalpha():
                self._addCertainty(10, "Primary domain is alphabetical with dashes.")

            if self.domain in ['google', 'amazon', 'github', 'imgur', 'wikipedia', 'youtube', 'stackoverflow']:
                self._addCertainty(15, "Primary domain is a popular site.")

        if self.tld:
            if not self.tld.isalpha():
                self._addCertainty(-25, "Top Level Domain is not alphabetical.")

            if self.tld == "com":
                self._addCertainty(40, "Top Level Domain '" + self.tld + "' is very commonly used.")

            if self.tld in ['co.uk', 'eu', 'info', 'me', 'net', 'org', 'uk', 'us']:
                self._addCertainty(30, "Top Level Domain '" + self.tld + "' is commonly used")

            if self.tld in ['c', 'cpp', 'css', 'exe', 'h', 'html', 'java', 'js', 'json', 'php', 'rb', 'sql']:
                self._addCertainty(-20, "Top Level Domain '" + self.tld + "' is a popular file extension.")

            if self.tld in ['pl', 'sh', 'so']:
                self.factors.append("[+0] Top Level Domain '" + self.tld + "' is either file extension or possible"
                                    " top level domain.")

        else:
            self._addCertainty(-50, "No top level domain found.")

        if self.port:
            if self.port == 80 or self.port == 443:
                self._addCertainty(25, "Port " + self.port + " is a standard HTTP/HTTPS port.")
            else:
                self._addCertainty(15, "Port " + self.port + " found.")

        if self.path:
            self._addCertainty(10, "Found path " + self.path)

        if urllib.parse.urlparse(self.url).netloc:
            self._addCertainty(25, "Python urllib parses as valid URL.")

        if self.certainty > Url.CERTAINTY_CAP:
            self.factors.append('[-' + str(self.certainty - Url.CERTAINTY_CAP) + '] Exceeds CERTAINTY_CAP.')
            self.certainty = Url.CERTAINTY_CAP

    def _addCertainty(self, amount, factor):
        """Adds amount of certainty and appends factor to the list of factors"""
        if amount == 0:
            return

        self.certainty += amount
        self.factors.append('[' + ('+' if amount > 0 else '') + str(amount) + '] ' + factor)
