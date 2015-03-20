#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.schema.member import Member


class MemberReference(Member):

    type = Member

    schemas = ()
    recursive = True

    MEMBERS = 1
    SCHEMAS = 2

    kind = MEMBERS | SCHEMAS

    def get_possible_values(self, context = None):

        values = Member.get_possible_values(self, context = context)

        if values is None and self.schemas:
            values = set()
            for schema in self.schemas:
                values.update(self.__iter_values_from_schema(schema))

        return values

    def __iter_values_from_schema(self, schema):

        if self.kind & self.SCHEMAS:
            yield schema

        if self.kind & self.MEMBERS:

            for member in schema.iter_members(recursive = True):
                yield member

        if self.recursive:
            derived_schemas = getattr(schema, "derived_schemas")
            if derived_schemas:
                for derived in derived_schemas(recursive = False):
                    for value in self.__iter_values_from_schema(derived):
                        yield value

