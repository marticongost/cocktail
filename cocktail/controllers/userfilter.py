#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from itertools import chain
from cocktail.modeling import getter, cached_getter
from cocktail.pkgutils import resolve
from cocktail.schema import (
    Schema,
    SchemaObject,
    Member,
    Number,
    BaseDateTime,
    String,
    Boolean,
    Collection,
    Reference,
    RelationMember
)
from cocktail.schema.expressions import (
    CustomExpression,
    Self,
    InclusionExpression,
    ExclusionExpression,
    GlobalSearchExpression,
    DescendsFromExpression,
    normalize
)
from cocktail.persistence import PersistentObject
from cocktail.html import templates
from cocktail.translations import translations

# TODO: Search can be used to indirectly access restricted members

# Extension property used to establish the user interface for a member in
# searches
Member.search_control = None


class UserFilter(object):

    id = None
    content_type = None
    available_languages = ()
    ui_class = "cocktail.html.UserFilterEntry"
    promoted_search = False
    repeatable = True
    search_control = None

    @cached_getter
    def schema(self):
        raise TypeError("Trying to access abstract property 'schema' on %s"
                        % self)

    @getter
    def expression(self):
        raise TypeError("Trying to access abstract property 'expression' on %s"
                % self)

    def create_ui(self):
        ui = templates.new(self.ui_class)
        ui.embeded = True
        ui.schema = self.schema
        ui.data = self
        return ui

    @getter
    def members(self):
        return ()


class MemberFilter(UserFilter):
    member = None
    value = None
    language = None

    @getter
    def members(self):
        return (self.member,)

    def _add_language_to_schema(self, schema):
        if self.member.translated:
            schema.add_member(String("language",
                required = True,
                enumeration = self.available_languages
            ))

    def _add_member_to_schema(self, schema):
        
        source_member = self.member

        if isinstance(source_member, Collection):
            source_member = source_member.items
        
        value_member = source_member.copy()
        value_member.name = "value"
        value_member.translated = False

        # Remove the bidirectional flag from relations
        if isinstance(value_member, RelationMember):
            value_member.bidirectional = False

        # Restricting relation cycles doesn't serve any purpose when collecting
        # the value of a user filter
        if isinstance(value_member, Reference):
            value_member.cycles_allowed = True

        schema.add_member(value_member)

    def _get_member_expression(self):
        if self.language:
            return self.member.translated_into(self.language)
        else:
            return self.member

    def __translate__(self, language, **kwargs):
        return translations(self.member, language, **kwargs)


class BooleanFilter(MemberFilter):
    
    repeatable = False

    @cached_getter
    def schema(self):
        schema = Schema()
        schema.name = "UserFilter"
        self._add_language_to_schema(schema)
        self._add_member_to_schema(schema)
        return schema

    @getter
    def expression(self):
        if self.value:
            return self._get_member_expression()
        else:
            return self._get_member_expression().not_()


class BinaryFilter(MemberFilter):
    
    operator = None
    operators = ()

    @cached_getter
    def schema(self):
        schema = Schema()
        schema.name = "UserFilter"
        self._add_language_to_schema(schema)
        schema.add_member(String("operator",
            required = True,
            enumeration = self.operators,
            default = self.operators[0] if self.operators else None
        ))
        self._add_member_to_schema(schema)
        return schema


class EqualityFilter(BinaryFilter):

    operators = ("eq", "ne")

    @getter
    def expression(self):
        if self.operator == "eq":
            return self._get_member_expression().equal(self.value)
        elif self.operator == "ne":
            return self._get_member_expression().not_equal(self.value)


class ComparisonFilter(EqualityFilter):

    operators = EqualityFilter.operators + ("gt", "ge", "lt", "le")
    
    @getter
    def expression(self):
        if self.operator == "gt":
            return self._get_member_expression().greater(self.value)
        elif self.operator == "ge":
            return self._get_member_expression().greater_equal(self.value)
        elif self.operator == "lt":
            return self._get_member_expression().lower(self.value)
        elif self.operator == "le":
            return self._get_member_expression().lower_equal(self.value)
        else:
            return EqualityFilter.expression.__get__(self)


class StringFilter(ComparisonFilter):

    operators = ComparisonFilter.operators + ("sr", "sw", "ew", "re")
    normalized_strings = True

    @getter
    def expression(self):
        
        if self.operator == "re":
            return self._get_member_expression().match(self.value)

        # Normalizable expressions
        if self.operator == "sr":
            expr = self._get_member_expression().search(self.value)
        elif self.operator == "sw":
            expr = self._get_member_expression().startswith(self.value)
        elif self.operator == "ew":
            expr = self._get_member_expression().endswith(self.value)
        else:
            expr = ComparisonFilter.expression.__get__(self)

        expr.normalized_strings = self.normalized_strings
        return expr


class GlobalSearchFilter(UserFilter):    
    id = "global_search"
    value = None
    language = None
    repeatable = False

    @cached_getter
    def schema(self):
        schema = Schema()
        schema.name = "UserFilter"
        
        if any(
            content_type.translated
            for content_type in chain(
                [self.content_type], self.content_type.derived_schemas()
            )
        ):        
            schema.members_order = ["value", "language"]
            schema.add_member(String("language",
                enumeration = self.available_languages
            ))

        schema.add_member(String("value", required = True))
        return schema

    @getter
    def expression(self):

        if self.language:
            languages = self.language,
        else:
            languages = self.available_languages

        return GlobalSearchExpression(self.value, languages)


class CollectionFilter(BinaryFilter):

    operators = ("cn", "nc")

    def _add_member_to_schema(self, schema):
        BinaryFilter._add_member_to_schema(self, schema)
        value_member = schema["value"]
        value_member.required = True

    @getter
    def expression(self):

        if self.member.bidirectional:

            related_value = self.value.get(self.member.related_end) or set()

            if isinstance(self.member.related_end, Collection):
                collection = related_value
            else:
                collection = set([related_value])

            if self.operator == "cn":
                return InclusionExpression(Self, collection)
            elif self.operator == "nc":
                return ExclusionExpression(Self, collection)
        else:
            if self.operator == "cn":
                return CustomExpression(lambda item:
                    self.value in (item.get(self.member) or set())
                )
            elif self.operator == "nc":
                return CustomExpression(lambda item:
                    self.value not in (item.get(self.member) or set())
                )


class MultipleChoiceFilter(MemberFilter):

    repeatable = False
    search_control = "cocktail.html.MultipleChoiceSelector"

    @cached_getter
    def schema(self):

        if isinstance(self.member, Reference):
            order = self.member.default_order
        elif isinstance(self.member, Collection):
            order = self.member.items.default_order

        return Schema("UserFilter", members = [
            Collection("values",
                items = Reference(
                    required = True,
                    type = self.member.related_type,
                    default_order = order
                ),
                min = 1,
                required = True
            )
        ])

    @getter
    def expression(self):

        member = self.member

        if not self.member.bidirectional \
        and isinstance(self.member, Collection):
            values = self.values
            expression = CustomExpression(
                lambda item: item.get(member) in values
            )

        else:
            subset = set()

            if isinstance(self.member, Reference):
                query = self.content_type.select
                by_key = True
                for value in self.values:
                    subset.update(
                        query(member.equal(value)).execute()
                    )
            
            elif isinstance(self.member, Collection):
                by_key = False
                rel_member = member.related_end
                for value in self.values:
                    subset.update(value.get(rel_member))
                
            expression = Self.one_of(subset)
            expression.by_key = by_key

        return expression


class DateTimeRangeFilter(UserFilter):

    id = "datetime_range"
    start_date_member = None
    end_date_member = None

    @getter
    def members(self):
        return (self.start_date_member, self.end_date_member)

    @cached_getter
    def schema(self):

        if self.start_date_member.__class__ \
        is not self.end_date_member.__class__:
            raise TypeError(
                "Different types for start_date_member and end_date_member"
            )
        
        start_date = self.start_date_member.copy()
        start_date.name = "start_date"

        end_date = self.end_date_member.copy()
        end_date.name = "end_date"

        return Schema("DateTimeRangeFilter", members = [start_date, end_date])

    @getter
    def expression(self):
    
        expression = None

        if self.start_date and self.end_date:
            expression = self.start_date_member.greater_equal(self.start_date) \
                         .and_(self.end_date_member.lower(self.end_date))
        elif self.start_date:
            expression = self.start_date_member.greater_equal(self.start_date)
        elif self.end_date:
            expression = self.end_date_member.lower(self.end_date)

        return expression


class DescendsFromFilter(UserFilter):
    id = "descends-from"
    relation = None

    @cached_getter
    def schema(self):
        
        return Schema("DescendsFromFilter", members = [
            Reference(
                "root",
                required = True,
                type = self.relation.schema
            ),
            Boolean(
                "include_self",
                required = True,
                default = True
            )
        ])

    @cached_getter
    def expression(self):
        return DescendsFromExpression(
            Self, self.root, self.relation, self.include_self
        )


# An extension property used to associate user filter types with members
Member.user_filter = EqualityFilter
Number.user_filter = ComparisonFilter
BaseDateTime.user_filter = ComparisonFilter
String.user_filter = StringFilter
Boolean.user_filter = BooleanFilter
Collection.user_filter = CollectionFilter

# An extension property used to determine which members should be searchable
Member.searchable = True

# An extension property used to determine which members should be looked at
# when doing a freeform text search. When set on a relation member searches
# will propagate across objects.
String.text_search = True
RelationMember.text_search = False

# An extension property used to determine which members have their search
# controls enabled by default
Member.promoted_search = False
Member.promoted_search_list = None

def _get_searchable_text(self, languages, visited_objects = None):

    if visited_objects is None:
        visited_objects = set()
    elif self in visited_objects:
        return
    
    visited_objects.add(self)

    # Concatenate all text fields
    for language in languages:
        for member in self.__class__.members().itervalues():
            if getattr(member, "text_search", False):
                member_value = self.get(member, language)
                if member_value:
                    if isinstance(member, String) and member.searchable:
                        yield member_value
                    elif isinstance(member, Reference):
                        for text in member_value.get_searchable_text(
                            languages,
                            visited_objects
                        ):
                            yield text
                    elif isinstance(member, Collection):
                        for child in member_value:
                            for text in child.get_searchable_text(
                                languages,
                                visited_objects
                            ):
                                yield text

SchemaObject.get_searchable_text = _get_searchable_text


class UserFiltersRegistry(object):

    def __init__(self):
        self.__filters_by_type = {}
        self.__filter_parameters = {}

    def get(self, content_type):
        
        filters_by_type = self.__filters_by_type
        filters = []

        # Custom filters
        for ancestor in content_type.descend_inheritance(include_self = True):
            ancestor_filters = filters_by_type.get(ancestor)
            if ancestor_filters:
                for filter_class in ancestor_filters:
                    filter = resolve(filter_class)()
                    self._init_filter(filter, content_type)
                    filters.append(filter)

        # Member filters
        for member in content_type.ordered_members():
            if member.searchable and member.user_filter and member.visible:
                filter = resolve(member.user_filter)()
                filter.id = "member-" + member.name
                filter.member = member
                self._init_filter(filter, content_type)
                filters.append(filter)

                if member.promoted_search:
                    filter.promoted_search = True

        return filters
    
    def _init_filter(self, filter, content_type):
        filter.content_type = content_type
        params = self.get_filter_parameters(content_type, filter.__class__)
        if params:
            for key, value in params.iteritems():
                setattr(filter, key, value)

    def add(self, cls, filter_class):
        class_filters = self.__filters_by_type.get(cls)
        if class_filters is None:
            class_filters = []
            self.__filters_by_type[cls] = class_filters
        
        class_filters.append(filter_class)

    def get_filter_parameters(self, cls, filter_class):

        params = {}

        for content_type in cls.descend_inheritance(include_self = True):
            content_type_params = \
                self.__filter_parameters.get((content_type, filter_class))
            if content_type_params:
                params.update(content_type_params)

        return params

    def set_filter_parameter(self, cls, filter_class, parameter, value):

        key = (cls, filter_class)
        params = self.__filter_parameters.get(key)

        if params is None:
            params = {}
            self.__filter_parameters[key] = params

        params[parameter] = value


user_filters_registry = UserFiltersRegistry()
user_filters_registry.add(PersistentObject, GlobalSearchFilter)

