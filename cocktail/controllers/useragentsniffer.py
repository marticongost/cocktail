#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
import cherrypy
from cocktail.modeling import SetWrapper


class UserAgentSniffer(object):

    def __init__(self, *patterns):
        self._patterns = SetWrapper()
        for pattern in patterns:
            self.add_pattern(pattern)

    @property
    def patterns(self):
        return self._patterns

    def add_pattern(self, pattern, flags = 0):

        if isinstance(pattern, basestring):
            pattern = re.compile(pattern, flags)

        self._patterns._items.add(pattern)

    def match(self, user_agent):
        return any(pattern.search(user_agent) for pattern in self._patterns)

    def match_request(self):

        key = "_user_agent_sniffer_%s" % id(self)
        match = getattr(cherrypy.request, key, None)

        if match is None:
            user_agent = cherrypy.request.headers.get("User-Agent")
            
            if user_agent is None:
                match = False
            else:
                match = self.match(user_agent)

            setattr(cherrypy.request, key, match)

        return match

    def __nonzero__(self):
        return self.match_request()


mobile_device = UserAgentSniffer(
    "Mobile",
    "Android",
    "iPhone",
    "iPod",
    "webOS",
    "Maemo"
)

