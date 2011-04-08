#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
def try_decode(text, encodings = ("utf8", "iso-8859-15")):                                                                                                                      
    for encoding in encodings:
        try:
            return unicode(text, encoding)
        except UnicodeDecodeError, e:
            pass

    raise e

