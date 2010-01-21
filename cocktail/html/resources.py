#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
from cocktail.modeling import getter

class Resource(object):
    
    mime_type = None
    extension = None
    _mime_type_register = {}
    _type_register = {}

    def __init__(self, uri):
        self.__uri = uri

    # Map file extensions to resource types
    class __metaclass__(type):

        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)

            mime_type = getattr(cls, "mime_type", None)
            
            if mime_type is not None:
                cls._mime_type_register[mime_type] = cls

            extension = getattr(cls, "extension", None)
            
            if extension is not None:
                cls._type_register[extension] = cls
            
    @classmethod
    def from_uri(cls, uri, mime_type = None):

        # By mime type
        if mime_type:
            resource_type = cls._mime_type_register.get(mime_type)
            if resource_type:
                resource = resource_type(uri)
                resource.mime_type = mime_type
                return resource

        # By extension
        else:
            for extension, resource_type in cls._type_register.iteritems():
                if uri.endswith(extension):
                    return resource_type(uri)
        
        raise ValueError(
            "Error handling resource: URI=%s, mime-type=%s" %
            (uri, mime_type)
        )

    @getter
    def uri(self):
        return self.__uri


class Script(Resource):
    extension = ".js"
    mime_type = "text/javascript"


class StyleSheet(Resource):
    extension = ".css"
    mime_type = "text/css"

