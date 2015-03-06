#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.schema.accessors import MemberAccessor
from cocktail.schema.schemaobject import SchemaObject


class SchemaObjectAccessor(MemberAccessor):
    """A member accessor for
    L{SchemaObject<cocktail.schema.schemaobject.SchemaObject>} instances, used
    by L{adapters<cocktail.schema.adapters.Adapter>} to retrieve and set object
    values.
    """

    @classmethod
    def get(cls, obj, key, default = _undefined, language = None):
        try:
            return obj.get(key, language)

        except AttributeError:
            if default is _undefined:
                raise

            return default

    @classmethod
    def set(cls, obj, key, value, language = None):
        obj.set(key, value, language)

    @classmethod
    def languages(cls, obj, key):
        if obj.__class__.translated:
            return obj.translations.keys()
        else:
            return (None,)

    @classmethod
    def can_handle(cls, obj):
        return isinstance(obj, SchemaObject)


SchemaObjectAccessor.register()

