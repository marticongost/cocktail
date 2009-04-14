#-*- coding: utf-8 -*-
"""Apply percent encoding to IRI fragments.

Adapted from a script by Joe Gregorio (joe@bitworking.org) under the MIT
license.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
"""

escape_range = [
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
    i = ord(c)
    for low, high in escape_range:
        if i < low:
            break
        if i <= high:
            return "".join("%%%2X" % ord(b) for b in c.encode('utf-8'))
    return c

