#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail.schema.member import Member
from cocktail.schema.schema import Schema
from cocktail.schema.schemarelations import RelationMember
from cocktail.schema.accessors import get_accessor, get
from cocktail.schema.expressions import HasExpression
from cocktail.schema.exceptions import (
    TypeCheckError,
    ClassFamilyError,
    RelationCycleError,
    RelationConstraintError
)
from .registry import import_type


class Reference(RelationMember):

    __class_family = None

    cycles_allowed = True
    default_order = "__auto__"
    include_root_schema = True

    def translate_value(self, value, language = None, **kwargs):
        if value is None:
            return RelationMember.translate_value(
                self, value, language, **kwargs
            )
        else:
            return translations(value, language, **kwargs)

    def _add_relation(self, obj, related_obj):
        get_accessor(obj).set(obj, self.name, related_obj)

    def _remove_relation(self, obj, related_obj):
        get_accessor(obj).set(obj, self.name, None)

    @property
    def related_type(self):
        return self.type

    def has(self, *args, **kwargs):

        filters = list(args)

        for key, value in kwargs.items():
            filters.append(self.related_type[key].equal(value))

        return HasExpression(self, filters)

    @event_handler
    def handle_attached_as_orphan(event):
        member = event.source
        member.type = member.related_end.schema

    # Validation
    #--------------------------------------------------------------------------
    def _get_class_family(self):

        # Resolve string references
        if isinstance(self.__class_family, str):
            self.__class_family = import_type(self.__class_family)

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

    def _default_validation(self, context):

        for error in RelationMember._default_validation(self, context):
            yield error

        if context.value is not None:

            # Apply the 'class_family' constraint
            class_family = \
                self.resolve_constraint(self.class_family, context)

            if class_family:
                if not isinstance(context.value, type):
                    yield TypeCheckError(context, type)
                elif not issubclass(context.value, class_family):
                    yield ClassFamilyError(context, class_family)
            else:
                # Apply the 'cycles_allowed' constraint
                if not self.cycles_allowed:
                    obj = get(context.value, self.name, None)
                    while obj:
                        if obj is context.value:
                            yield RelationCycleError(context)
                            break
                        obj = get(obj, self.name, None)

                # Apply relation constraints
                relation_constraints = \
                    self.resolve_constraint(self.relation_constraints, context)

                if hasattr(relation_constraints, "items"):
                    constraints_mapping = relation_constraints
                    relation_constraints = (
                        self.type.get_member(key).equal(value)
                        for key, value in constraints_mapping.items()
                    )

                if relation_constraints:
                    owner = context.get_object()
                    for constraint in relation_constraints:
                        if not self.validate_relation_constraint(
                            constraint,
                            owner,
                            context.value
                        ):
                            yield RelationConstraintError(context, constraint)

    def extract_searchable_text(self, extractor):
        item = extractor.current.value.__class__
        return item.extract_searchable_text(extractor)

    def get_possible_values(self, context = None):

        values = RelationMember.get_possible_values(self, context)

        if values is None:
            if self.class_family:
                if isinstance(self.class_family, Schema):
                    values = list(
                        self.class_family.schema_tree()
                        if self.include_root_schema
                        else self.class_family.derived_schemas()
                    )

        if values is None or self.default_order:
            if self.type is not None:
                if hasattr(self, "select_constraint_instances"):
                    query = self.select_constraint_instances(
                        parent = context and context.get("persistent_object")
                    )
                elif hasattr(self.type, "select"):
                    query = self.type.select()

                if values is not None:
                    query.base_collection = values

                order = self.default_order

                if order == "__auto__":
                    order = getattr(self.type, "descriptive_member", None)

                if order is not None:
                    if isinstance(order, (str, Member)):
                        query.add_order(order)
                    else:
                        for criteria in order:
                            query.add_order(criteria)

                values = query

        return values

