#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""

undefined = object()


def get_accessor(obj):

    if isinstance(obj, dict):
        return DictAccessor
    else:
        return AttributeAccessor


class MemberAccessor(object):

    @classmethod
    def get(cls, obj, key, default = undefined, language = None):
        """Gets a value from the indicated object.
        
        @param obj: The object to get the value from.
        @type obj: object

        @param key: The name of the value to retrieve.
        @type key: str

        @param default: Provides a the default value that will be returned in
            case the supplied object doesn't define the requested key. If this
            parameter is not set, a KeyError exception will be raised.            

        @param language: Required for multi-language values. Indicates the
            language to retrieve the value in.
        @type language: str
    
        @return: The requested value, if defined. If not, the method either
            returns the default value (if one has been specified) or raises a
            KeyError exception.

        @raise KeyError: Raised when an attempt is made to access an undefined
            key, and no default value is provided.
        """

    @classmethod
    def set(cls, obj, key, value, language = None):
        """Sets the value of a key on the indicated object.
        
        @param obj: The object to set the value on.
        @type obj: object

        @param key: The key to set.
        @type key: str

        @param language: Required for multi-language values. Indicates the
            language that the value is assigned to.
        @type language: str
        """

    @classmethod
    def languages(cls, obj, key):
        """Determines the set of languages that the given object key is
        translated into.
        
        @param obj: The object to evaluate.
        @type obj: object

        @param key: The key to evaluate.
        @type key: str

        @return: A sequence or set of language identifiers.
        @rtype: str iterable
        """


class DictAccessor(MemberAccessor):

    @classmethod
    def get(cls, obj, key, default = undefined, language = None):

        if language:
            translation = obj.get(key)
            
            if translation is None:
                value = undefined
            else:
                value = translation.get(language, undefined)
        else:
            value = obj.get(key, undefined)

        if value is undefined:
            raise KeyError(key)

        return value

    @classmethod
    def set(cls, obj, key, value, language = None):
        if language:
            translation = obj.get(key)
            if translation is None:
                obj[key] = translation = {}
            translation[language] = value
        else:        
            obj[key] = value

    @classmethod
    def languages(cls, obj, key):
        items = obj.get(key)
        return items.iterkeys() if items else ()


class AttributeAccessor(MemberAccessor):

    @classmethod
    def get(cls, obj, key, default = undefined, language = None):        
        if language:
            raise ValueError(
                "AttributeAccessor can't operate on translated members")
        else:
            if default is undefined:
                return getattr(obj, key)
            else:
                return getattr(obj, key, default)

    @classmethod
    def set(cls, obj, key, value, language = None):
        if language:
            raise ValueError(
                "AttributeAccessor can't operate on translated members")
        else:
            setattr(obj, key, value)

    @classmethod
    def languages(cls, obj, key):
        return None,

