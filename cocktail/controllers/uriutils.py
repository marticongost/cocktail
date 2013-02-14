#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from decimal import Decimal
from urllib import quote


def make_uri(*args, **kwargs):

    uri = u"/".join(unicode(arg).strip(u"/") for arg in args)

    if kwargs:
        params = []

        for pair in kwargs.iteritems():
            if pair[1] is None:
                continue
            elif isinstance(pair[1], (
                basestring,
                int,
                float,
                Decimal
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

