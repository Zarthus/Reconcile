"""
Debug URLs by Zarthus
Licensed under MIT
"""

from core import moduletemplate
from tools import url


class UrlDebug(moduletemplate.BotModule):

    def on_module_load(self):
        self.register_command("isurl", "<url>", "Validate an URL through the Url class.", self.PRIV_ADMIN)
        self.register_command("findurl", "<url>", "Validate an URL through the Url class.", self.PRIV_ADMIN)
        self.register_command("dumpurl", "<url>", "Dump information about an URL", self.PRIV_ADMIN)
        self.register_command("urlstring", "<string>", "Validate multiple URLs through the Url class.",
                              self.PRIV_ADMIN)

    def on_command(self, target, nick, command, commandtext, mod, admin):
        if admin:
            if command == "isurl":
                if not commandtext:
                    return self.notice(nick, "Usage: isurl <url>")

                link = commandtext

                urlclass = url.Url(link)

                self.log(str(urlclass.getAsDict()))
                self.message(target, nick, ("{}: {}/{} certain, {}"
                                            .format(urlclass.getUrl(),
                                                    urlclass.getCertainty(),
                                                    urlclass.getMinCertainty(),
                                                    str(urlclass.getFactors()))))

                return True

            if command == "findurl":
                if not commandtext:
                    return self.notice(nick, "Usage: findurl <string>")

                u = url.Url.find(commandtext)
                if not u:
                    return self.message(target, nick, "no matches")

                self.log(str(u.getAsDict()))

                self.message(target, nick, ("{}: {}/{} certain, {}"
                                            .format(u.getUrl(),
                                                    u.getCertainty(),
                                                    u.getMinCertainty(),
                                                    str(u.getFactors()))))
                return True

            if command == "dumpurl":
                if not commandtext:
                    return self.notice(nick, "Usage: dumpurl <string>")

                u = url.Url.find(commandtext)
                if not u:
                    return self.message(target, nick, "no matches")

                self.message(target, nick, str(u.getAsDict()))
                return True

            if command == "urlstring":
                if not commandtext:
                    return self.notice(nick, "Usage: urlstring <string>")

                urllist = url.Url.findAll(commandtext)
                if not urllist:
                    return self.message(target, nick, "no matches")

                for u in urllist:
                    self.log(str(u.getAsDict()))
                    self.message(target, nick, ("{}: {}/{} certain, {}"
                                                .format(u.getUrl(),
                                                        u.getCertainty(),
                                                        u.getMinCertainty(),
                                                        str(u.getFactors()))))
                return True

        return False
