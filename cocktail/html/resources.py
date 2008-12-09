#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
from cocktail.modeling import getter

class Resource(object):
    
    mime_type = None
    extension = None
    _type_register = {}

    def __init__(self, uri):
        self.__uri = uri

    # Map file extensions to resource types
    class __metaclass__(type):

        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)

            extension = getattr(cls, "extension", None)
            
            if extension is not None:
                cls._type_register[extension] = cls

    @classmethod
    def from_uri(cls, uri):
        for extension, resource_type in cls._type_register.iteritems():
            if uri.endswith(extension):
                return resource_type(uri)
        else:
            raise ValueError("No matching resource type for '%s'" % uri)

    @getter
    def uri(self):
        return self.__uri


class Script(Resource):
    extension = ".js"
    mime_type = "text/javascript"


class StyleSheet(Resource):
    extension = ".css"
    mime_type = "text/css"

