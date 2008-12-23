#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail.modeling import getter
from cocktail.pkgutils import import_object
from cocktail.schema.schemarelations import RelationMember
from cocktail.schema.accessors import get_accessor
from cocktail.schema.exceptions import ClassFamilyError


class Reference(RelationMember):
    
    __class_family = None

    def __init__(self, *args, **kwargs):
        RelationMember.__init__(self, *args, **kwargs)
        self.add_validation(self.__class__.reference_validation_rule)

    def _add_relation(self, obj, related_obj):
        get_accessor(obj).set(obj, self.name, related_obj)                

    def _remove_relation(self, obj, related_obj):
        get_accessor(obj).set(obj, self.name, None)

    @getter
    def related_type(self):
        return self.type

    # Validation
    #--------------------------------------------------------------------------
    def _get_class_family(self):

        # Resolve string references
        if isinstance(self.__class_family, basestring):
            self.__class_family = import_object(self.__class_family)

        return self.__class_family

    def _set_class_family(self, class_family):
        self.__class_family = class_family

    class_family = property(_get_class_family, _set_class_family, doc = """
        Imposes a data type constraint on the member. All values assigned to
        this member must be subclasses of the specified class (a reference to
        that same class is also acceptable). Breaking this restriction will
        produce a validation error of type
        L{ClassFamilyError<exceptions.ClassFamilyError>}.
        @type type: type or str
        """)

    def reference_validation_rule(self, value, context):

        if value and isinstance(value, type):

            class_family = \
                self.resolve_constraint(self.class_family, context)

            if class_family and not issubclass(value, class_family):
                yield ClassFamilyError(self, value, context, class_family)

