#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""

def make_uri(*args, **kwargs):

    uri = u"/".join(unicode(arg).strip(u"/") for arg in args)

    if kwargs:
        params = []

        for pair in kwargs.iteritems():
            if isinstance(pair[1], basestring):
                params.append(pair)
            else:
                for item in pair[1]:
                    params.append(pair[0], item)

        uri += "?" + "&".join("%s=%s" % pair for pair in params.iteritems())

    return uri

def try_decode(text, encodings = ("utf8", "iso-8859-15")):
    for encoding in encodings:
        try:
            return unicode(text, encoding)
        except UnicodeDecodeError, e:
            pass

    raise e
