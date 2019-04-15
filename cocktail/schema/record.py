"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .member import Member
from .registry import import_type


class Record(Member):

    type = dict

    def _default_validation(self, context):

        yield from Member._default_validation(self, context)

        if self.record_schema and context.validable is not None:
            yield from self.record_schema.get_errors(
                context.validable,
                parent_context=context
            )

    def to_json_value(self, value, **options):

        if value is not None and self.record_schema:
            return self.record_schema.to_json_value(value, **options)

        return value

    def from_json_value(self, value, **options):

        if value is not None and self.record_schema:
            return self.record_schema.from_json_value(value, **options)

        return value

    def _get_record_schema(self):
        if isinstance(self.__record_schema, str):
            if self._schema:
                self.__record_schema = import_type(self.__record_schema)
        return self.__record_schema

    def _set_record_schema(self, value):
        self.__record_schema = value

    record_schema = property(_get_record_schema, _set_record_schema)

