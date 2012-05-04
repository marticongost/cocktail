#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from random import choice
from string import letters, digits

normalization_map = {}

def create_translation_map(pairs):

    translation_map = {}

    iteritems = getattr(pairs, "iteritems", None)
    if iteritems is not None:
        pairs = iteritems()

    for repl, chars in pairs:
        for c in chars:
            translation_map[ord(c)] = ord(repl)

    return translation_map

_normalization_map = create_translation_map({
    u"a": u"áàäâ",
    u"e": u"éèëê",
    u"i": u"íìïî",
    u"o": u"óòöô",
    u"u": u"úùüû",
    u" ": u"'\"\t\n\r(),.:;+-*/\\¡!¿?&|=[]{}~#¬<>"
})

def normalize(string):
    string = string.lower()

    if not isinstance(string, unicode):
        try:
	    string = unicode(string)
	except:
	    return string

    if isinstance(string, unicode):
        string = string.translate(_normalization_map)
        string = u" ".join(string.split())

    return string

def random_string(length, source = letters + digits + "!?.-$#&@*"):
    return "".join(choice(source) for i in xrange(length))

