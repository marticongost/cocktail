#-*- coding: utf-8 -*-
"""
Provides a class to describe members that handle sets of values.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.schema.schemacollections import Collection

class Mapping(Collection):
    """A collection that handles a set of key and value associations.

    @ivar keys: The schema that all keys in the collection must comply with.
        Specified as a member, which will be used as the validator for all
        values added to the collection.
    @type: L{Member<member.Member>}
    
    @ivar values: The schema that all values in the collection must comply
        with. Specified as a member, which will be used as the validator for
        all values added to the collection.
    @type: L{Member<member.Member>}
    """
    keys = None
    values = None
    default_type = dict

    def items_validation_rule(self, value, context):

        if value is not None:

            # Item validation
            keys = self.resolve_constraint(self.keys, context)
            values = self.resolve_constraint(self.values, context)

            if keys is not None or values is not None:
                
                context.enter(self, value)
    
                try:
                    for key, value in value.iteritems():
                        if keys is not None:
                            for error in keys.get_errors(key, context):
                                yield error
                        if values is not None:
                            for error in values.get_errors(value, context):
                                yield error
                finally:
                    context.leave()

