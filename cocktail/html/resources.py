#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
from cocktail.modeling import getter

class Resource(object):
    
    default_mime_type = None
    mime_types = {}
    extensions = {}

    def __init__(self, uri, mime_type = None, ie_condition = None):
        self.__uri = uri
        self.__mime_type = mime_type or self.default_mime_type
        self.__ie_condition = ie_condition
           
    @classmethod
    def from_uri(cls, uri, mime_type = None, ie_condition = None):

        resource_type = None

        # By mime type
        if mime_type:
            resource_type = cls.mime_types.get(mime_type)

        # By extension
        else:
            for extension, resource_type in cls.extensions.iteritems():
                if uri.endswith(extension):
                    break
            else:
                resource_type = None

        if resource_type is None:
            raise ValueError(
                "Error handling resource: URI=%s, mime-type=%s"
                % (uri, mime_type)
            )

        return resource_type(
            uri, 
            mime_type = mime_type,
            ie_condition = ie_condition
        )

    @getter
    def uri(self):
        return self.__uri

    @getter
    def mime_type(self):
        return self.__mime_type

    @getter
    def ie_condition(self):
        return self.__ie_condition

    def __hash__(self):
        return hash(self.uri + self.mime_type + (self.ie_condition or ""))

    def __eq__(self, other):
        return self.__class__ is other.__class__ \
           and self.uri == other.uri \
           and self.mime_type == other.mime_type \
           and self.ie_condition == other.ie_condition


class Script(Resource):
    default_mime_type = "text/javascript"


class StyleSheet(Resource):
    default_mime_type = "text/css"


Resource.extensions[".js"] = Script
Resource.extensions[".css"] = StyleSheet
Resource.extensions[".sss"] = StyleSheet
Resource.mime_types["text/javascript"] = Script
Resource.mime_types["text/css"] = StyleSheet
Resource.mime_types["text/switchcss"] = StyleSheet

