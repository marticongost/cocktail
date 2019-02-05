#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from itertools import chain
from cocktail.modeling import getter, cached_getter
from cocktail.pkgutils import resolve
from cocktail.translations import translations
from cocktail import schema
from cocktail.schema.expressions import (
    CustomExpression,
    Self,
    InclusionExpression,
    ExclusionExpression,
    DescendsFromExpression,
    normalize
)
from cocktail.persistence import PersistentObject
from cocktail.controllers import viewstate
from cocktail.controllers.parameters import serialize_parameter
from cocktail.html import templates
from cocktail.translations import translations, translate_locale

translations.load_bundle("cocktail.controllers.userfilter")

# TODO: Search can be used to indirectly access restricted members

# Extension property used to establish the user interface for a member in
# searches
schema.Member.search_control = None


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

    def _add_language_to_schema(self, target_schema):
        if self.member.translated:
            target_schema.add_member(
                schema.String(
                    "language",
                    required = True,
                    enumeration = self.available_languages,
                    translate_value = (
                        lambda value, language = None, **kwargs:
                            "" if not value
                            else translate_locale(value, language = language)
                    ),
                    search_control = "cocktail.html.DropdownSelector"
                )
            )

    def _add_member_to_schema(self, target_schema):

        source_member = self.member

        if isinstance(source_member, schema.Collection):
            source_member = source_member.items

        value_member = source_member.copy()
        value_member.name = "value"
        value_member.translated = False
        value_member.default = None
        value_member.editable = schema.EDITABLE

        # Remove the bidirectional flag from relations
        if isinstance(value_member, schema.RelationMember):
            value_member.bidirectional = False

        # Restricting relation cycles doesn't serve any purpose when collecting
        # the value of a user filter
        if isinstance(value_member, schema.Reference):
            value_member.cycles_allowed = True

        target_schema.add_member(value_member)

    def _get_member_expression(self):
        if self.language:
            return self.member.translated_into(self.language)
        else:
            return self.member


class BooleanFilter(MemberFilter):

    repeatable = False

    @cached_getter
    def schema(self):
        filter_schema = schema.Schema()
        filter_schema.name = "cocktail.controllers.userfilter.BooleanFilter"
        self._add_language_to_schema(filter_schema)
        self._add_member_to_schema(filter_schema)
        return filter_schema

    @getter
    def expression(self):
        if self.value:
            return self._get_member_expression().equal(True)
        else:
            return self._get_member_expression().equal(False)


class BinaryFilter(MemberFilter):

    operator = None
    operators = ()

    @cached_getter
    def schema(self):
        filter_schema = schema.Schema()
        filter_schema.name = "cocktail.controllers.userfilter.BinaryFilter"
        self._add_language_to_schema(filter_schema)
        filter_schema.add_member(
            schema.String("operator",
                required = True,
                enumeration = self.operators,
                default = self.operators[0] if self.operators else None,
                search_control = "cocktail.html.DropdownSelector"
            )
        )
        self._add_member_to_schema(filter_schema)
        return filter_schema


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

    @cached_getter
    def schema(self):
        filter_schema = ComparisonFilter.schema(self)
        # Remove validations
        value = filter_schema.get_member("value")
        value.min = value.max = value.format = None
        return filter_schema

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
        filter_schema = schema.Schema()
        filter_schema.name = "cocktail.controllers.userfilter.GlobalSearchFilter"

        if any(
            content_type.translated
            for content_type in chain(
                [self.content_type], self.content_type.derived_schemas()
            )
        ):
            filter_schema.members_order = ["value", "language"]
            filter_schema.add_member(
                schema.String("language",
                    enumeration = self.available_languages,
                    translate_value = (
                        lambda value, language = None, **kwargs:
                        "" if not value
                        else translations(
                            "cocktail.controllers.userfilter.GlobalSearchFilter.translated_into",
                            locale = value,
                            language = language
                        )
                    )
                )
            )

        filter_schema.add_member(schema.String("value", required = True))
        return filter_schema

    @getter
    def expression(self):

        if not self.value:
            return None

        if self.language:
            languages = self.language,
        else:
            languages = self.available_languages

        if None not in languages:
            languages = [None] + list(languages)

        return Self.search(self.value, languages = languages)


class CollectionFilter(BinaryFilter):

    operators = ("cn", "nc")

    def _add_member_to_schema(self, target_schema):
        BinaryFilter._add_member_to_schema(self, target_schema)
        value_member = target_schema["value"]
        value_member.required = True

    @getter
    def expression(self):

        if self.member.bidirectional:

            related_value = self.value.get(self.member.related_end)

            if isinstance(self.member.related_end, schema.Collection):
                collection = related_value or set()
            else:
                collection = set() if related_value is None else related_value

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

        return schema.Schema(
            "cocktail.controllers.userfilter.DateTimeRangeFilter",
            members = [start_date, end_date]
        )

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

        return schema.Schema(
            "cocktail.controllers.userfilter.DescendsFromFilter",
            members = [
                schema.Reference(
                    "root",
                    required = True,
                    type = self.relation.schema
                ),
                schema.Boolean(
                    "include_self",
                    required = True,
                    default = True
                )
            ]
        )

    @cached_getter
    def expression(self):
        return DescendsFromExpression(
            Self, self.root, self.relation, self.include_self
        )


# An extension property used to associate user filter types with members
schema.Member.user_filter = EqualityFilter
schema.Number.user_filter = ComparisonFilter
schema.BaseDateTime.user_filter = ComparisonFilter
schema.String.user_filter = StringFilter
schema.Boolean.user_filter = BooleanFilter
schema.Collection.user_filter = CollectionFilter

# An extension property used to determine which members should be searchable
schema.Member.searchable = True

# An extension property used to determine which members have their search
# controls enabled by default
schema.Member.promoted_search = False
schema.Member.promoted_search_list = None


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
                filter = self._create_member_filter(content_type, member)
                filters.append(filter)

        return filters

    def _create_member_filter(self, content_type, member):
        filter = resolve(member.user_filter)()
        filter.id = "member-" + member.name
        filter.member = member
        self._init_filter(filter, content_type)
        if member.promoted_search:
            filter.promoted_search = True
        return filter

    def _init_filter(self, filter, content_type):
        filter.content_type = content_type
        params = self.get_filter_parameters(content_type, filter.__class__)
        if params:
            for key, value in params.items():
                setattr(filter, key, value)

    def get_new_filter_view_state(self, content_type, filters, new_filter):

        if isinstance(new_filter, schema.Member):
            new_filter = self._create_member_filter(content_type, new_filter)

        index = len(filters)
        filters = list(filters)
        filters.append(new_filter.id)

        state = viewstate.get_state()
        state["filter"] = filters

        for member in new_filter.schema.iter_members():
            value = getattr(new_filter, member.name)
            if value is None:
                value = ""
            else:
                value = serialize_parameter(member, value)
            state["filter_%s%d" % (member.name, index)] = value

        return state

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

# Translation
#------------------------------------------------------------------------------
@translations.instances_of(MemberFilter)
def translate_member_filter(member_filter, **kwargs):
    return translations(member_filter.member, **kwargs)

