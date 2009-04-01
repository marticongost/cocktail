#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
undefined = object()
_accessors = []


def get_accessor(obj):
    for accessor in _accessors:
        if accessor.can_handle(obj):
            return accessor

def get(obj, key, default = undefined, language = None):
    
    if not isinstance(key, basestring):
        key = key.name
    
    accessor = get_accessor(obj)
    return accessor.get(obj, key, default, language)

def set(obj, key, value, language = None):
    
    if not isinstance(key, basestring):
        key = key.name
    
    accessor = get_accessor(obj)
    accessor.set(obj, key, value, language)


class MemberAccessor(object):

    @classmethod
    def register(cls):
        """Registers the accessor, so that it can be taken into account by the
        L{get_accessor} function.
        """
        _accessors.insert(0, cls)

    @classmethod
    def can_handle(cls, obj):
        """Indicates if the accessor can handle the provided object.
        
        @param obj: The object to evaluate.
        
        @return: True if the accessor is able to operate on the object, False
            otherwise.
        """
        
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
    

class AttributeAccessor(MemberAccessor):

    @classmethod
    def can_handle(cls, obj):
        return True

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


class DictAccessor(MemberAccessor):

    @classmethod
    def can_handle(cls, obj):
        return isinstance(obj, dict)

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
            value = default

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


AttributeAccessor.register()
DictAccessor.register()

