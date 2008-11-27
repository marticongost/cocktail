#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.modeling import getter, cached_getter
from cocktail.schema import (
    Schema, Member, Number, BaseDateTime, String, Boolean
)
from cocktail.html import templates
from cocktail.translations import translate


def get_content_type_filters(content_type):

    filters = []

    for member in content_type.ordered_members():
        if member.user_filter and member.visible:
            filter = member.user_filter()
            filter.id = "member-" + member.name
            filter.member = member
            filters.append(filter)
    
    return filters


class UserFilter(object):

    id = None
    available_languages = ()
    ui_class = "cocktail.html.UserFilterEntry"
   
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


class MemberFilter(UserFilter):
    member = None
    value = None
    language = None

    def _add_language_to_schema(self, schema):
        if self.member.translated:
            schema.add_member(String("language",
                required = True,
                enumeration = self.available_languages
            ))

    def _add_member_to_schema(self, schema):
        value_member = self.member.copy()
        value_member.name = "value"
        value_member.translated = False
        schema.add_member(value_member)

    def _get_member_expression(self):
        if self.language:
            return self.member.translated_into(self.language)
        else:
            return self.member

    def __translate__(self, language, **kwargs):
        return translate(self.member, language, **kwargs)


class BooleanFilter(MemberFilter):
    
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
            enumeration = self.operators)
        )
        self._add_member_to_schema(schema)
        return schema


class EqualityFilter(BinaryFilter):

    operators = ("eq", "ne")

    @getter
    def expression(self):
        if self.operator == "eq":
            return self._get_member_expression() == self.value
        elif self.operator == "ne":
            return self._get_member_expression() != self.value


class ComparisonFilter(EqualityFilter):

    operators = EqualityFilter.operators + ("gt", "ge", "lt", "le")
    
    @getter
    def expression(self):
        if self.operator == "gt":
            return self._get_member_expression() > self.value
        elif self.operator == "ge":
            return self._get_member_expression() >= self.value
        elif self.operator == "lt":
            return self._get_member_expression() < self.value
        elif self.operator == "le":
            return self._get_member_expression() <= self.value
        else:
            return EqualityFilter.expression.__get__(self)


class StringFilter(ComparisonFilter):

    operators = ComparisonFilter.operators + ("sr", "sw", "ew", "re")

    @getter
    def expression(self):
        if self.operator == "sr":
            return self._get_member_expression().search(self.value)
        elif self.operator == "sw":
            return self._get_member_expression().startswith(self.value)
        elif self.operator == "ew":
            return self._get_member_expression().endswith(self.value)
        elif self.operator == "re":
            return self._get_member_expression().match(self.value)


# An extension property used to associate user filter types with members
Member.user_filter = EqualityFilter
Number.user_filter = ComparisonFilter
BaseDateTime.user_filter = ComparisonFilter
String.user_filter = StringFilter
Boolean.user_filter = BooleanFilter

