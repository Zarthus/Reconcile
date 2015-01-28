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

paste.py by Zarthus,
Licensed under MIT
"""

import requests
import json


class Paste:
    """
    paste.py: Serveral methods to store text online.

    All methods in this class are 'static' and support the 'logger' parameter,
    Whenever possible, passing this parameter ensures errors will be logged to console, so it is recommended you do.
    """

    def gist(description, content, filename="ircgist.txt", public=False, logger=None):
        """
        Post a gist to https://gist.github.com

        description: string, Description for your gist.
        content: string, content to paste.
        filename: string, filename.ext - name of file and extension
        public: boolean, should your gist be visible to public or not.
        logger: Logger, an instance of the logger class.

        returns link of your gist or False on failure.
        If logger is passed an Error will be logged to console.

        For more information, reference to https://developer.github.com/v3/gists/#create-a-gist
        """

        url = "https://api.github.com/gists"
        payload = {
            "description": description,
            "public": public,
            "files": {
                filename: {
                    "content": content
                }
            }
        }

        returnurl = ""

        try:
            r = requests.post(url, data=json.dumps(payload))

            if r.ok and "html_url" in r.json():
                returnurl = r.json()["html_url"]
            else:
                r.raise_for_status()
        except Exception as e:
            if logger:
                logger.error("Error creating gist '{}': {}".format(filename, str(e)))

        if returnurl:
            return returnurl
        return False

    def gist_multifile(description, files, public=False, logger=None):
        """
        Upload multiple gists https://gist.github.com

        description: string, Description for your gist.
        content: string, content to paste.
        files: dict, following format: {"filename.ext": {"content": "the contents of your file"}}
        public: boolean, should your gist be visible to public or not.
        logger: Logger, an instance of the logger class.

        returns link of your gist or False on failure.
        If logger is passed an Error will be logged to console.

        For more information, reference to https://developer.github.com/v3/gists/#create-a-gist
        """

        url = "https://api.github.com/gists"
        payload = {
            "description": description,
            "public": public,
            "files": {
                files
            }
        }

        returnurl = ""

        try:
            r = requests.post(url, data=json.dumps(payload))

            if r.ok and "html_url" in r.json():
                returnurl = r.json()["html_url"]
            else:
                r.raise_for_status()
        except Exception as e:
            if logger:
                logger.error("Error creating gist multifile: {}".format(str(e)))

        if returnurl:
            return returnurl
        return False
