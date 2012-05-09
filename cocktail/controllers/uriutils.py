#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from decimal import Decimal
from fractions import Fraction
from urllib import quote


def make_uri(*args, **kwargs):

    uri = u"/".join(unicode(arg).strip(u"/") for arg in args)

    if kwargs:
        params = []

        for pair in kwargs.iteritems():
            if isinstance(pair[1], (
                basestring,
                int,
                float,
                Decimal,
                Fraction
            )):
                params.append(pair)
            else:
                for item in pair[1]:
                    params.append((pair[0], item))
        
        uri += u"?" + u"&".join(
            ("%s=%s" % (
                name,
                quote(
                    value.encode("utf-8") 
                    if isinstance(value, unicode) 
                    else str(value)
                )
            )).decode("utf-8")
            for name, value in params
        )

    return uri

def try_decode(text, encodings = ("utf8", "iso-8859-15")):
    for encoding in encodings:
        try:
            return unicode(text, encoding)
        except UnicodeDecodeError, e:
            pass

    raise e

percent_encode_escape_range = [
   (0xA0, 0xD7FF),
   (0xE000, 0xF8FF),
   (0xF900, 0xFDCF),
   (0xFDF0, 0xFFEF),
   (0x10000, 0x1FFFD),
   (0x20000, 0x2FFFD),
   (0x30000, 0x3FFFD),
   (0x40000, 0x4FFFD),
   (0x50000, 0x5FFFD),
   (0x60000, 0x6FFFD),
   (0x70000, 0x7FFFD),
   (0x80000, 0x8FFFD),
   (0x90000, 0x9FFFD),
   (0xA0000, 0xAFFFD),
   (0xB0000, 0xBFFFD),
   (0xC0000, 0xCFFFD),
   (0xD0000, 0xDFFFD),
   (0xE1000, 0xEFFFD),
   (0xF0000, 0xFFFFD),
   (0x100000, 0x10FFFD)
]
 
def percent_encode(c):
    """Apply percent encoding to IRI fragments.

    Adapted from a script by Joe Gregorio (joe@bitworking.org) under the MIT
    license.
    """
    i = ord(c)
    for low, high in percent_encode_escape_range:
        if i < low:
            break
        if i <= high:
            return "".join("%%%2X" % ord(b) for b in c.encode('utf-8'))
    return c

def percent_encode_uri(uri):
    return "".join(percent_encode(c) for c in uri)

