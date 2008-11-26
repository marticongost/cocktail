#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from copy import copy
from cocktail.modeling import getter
from cocktail.html import templates
from cocktail import schema


class UserFilter(object):

    filter_type_id = None
    available_languages = ()
    ui_class = "html.cocktail.Form"
   
    @getter
    def schema(self):
        pass

    @getter
    def expression(self):
        pass

    def create_ui(self):
        ui = templates.get_class(self.ui_class)
        ui.embeded = True
        ui.schema = self.get_schema()
        ui.data = self
        return ui


class MemberFilter(UserFilter):
    member = None
    value = None
    language = None

    def _add_language_to_schema(self, schema):
        if self.member.translated:
            language_member = String("language",
                enumeration = self.available_languages)
            schema.add(language_member)

    def _add_member_to_schema(self, schema):
        value_member = copy(self.member)
        value_member.name = "value"
        schema.add(value_member)

    def _get_member_expression(self):
        if self.language:
            return self.member.translated_into(self.language)
        else:
            return self.member


class BooleanFilter(MemberFilter):

    filter_type_id = "bool"

    @getter
    def schema(self):
        schema = Schema()
        
        return schema
    
    @getter
    def schema(self):
        schema = Schema()
        self._add_language_to_schema(schema)
        self._add_member_to_schema(schema)
        return schema

    @getter
    def expression(self):
        return self._get_member_expression() == self.value


class BinaryFilter(MemberFilter):
    
    operator = None
    operators = ()

    @getter
    def schema(self):

        schema = Schema()
        self._add_language_to_schema(schema)
        schema.add(schema.String("operator", enumeration = self.operators))
        self._add_member_to_schema(schema)
        return schema


class EqualityFilter(BinaryFilter):

    filter_type_id = "eq"
    operators = ("eq", "ne")

    @getter
    def expression(self):
        if self.operator == "eq":
            return self._get_member_expression() == self.value
        elif self.operator == "ne":
            return self._get_member_expression() != self.value


class ComparisonFilter(EqualityFilter):

    filter_type_id = "cmp"
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
        elsE:
            return EqualityFilter.expression.__get__(self)


class StringFilter(ComparisonFilter):

    filter_type_id = "str"
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
schema.Member.user_filter = EqualityFilter
schema.String.user_filter = StringFilter
schema.RangedMember.user_filter = ComparisonFilter
schema.Boolean.user_filter = BooleanFilter

