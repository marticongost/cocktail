#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""


class CacheSerializer(object):

    def serialize(self, obj):
        raise TypeError(
            "%s doesn't implement the serialize() method" % self
        )

    def unserialize(self, obj):
        raise TypeError(
            "%s doesn't implement the unserialize() method" % self
        )

