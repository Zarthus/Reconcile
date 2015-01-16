"""
UrlTools: Interact and manipulate URLs
"""


class UrlTools:

    def shorten(url, service=None):
        if not service:
            service = UrlTools.getDefaultShortenService()
        pass

    def getDefaultShortenService():
        pass

    def getTitle(url):
        pass
