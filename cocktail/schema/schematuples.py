#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.schema.member import Member
from cocktail.schema.exceptions import MinItemsError, MaxItemsError


class Tuple(Member):

    type = tuple
    items = ()

    def _default_validation(self, context):

        for error in Member._default_validation(self, context):
            yield error

        if context.value is not None:

            value_length = len(context.value)
            expected_length = len(self.items)

            if value_length < expected_length:
                yield MinItemsError(context, expected_length)

            elif value_length > expected_length:
                yield MaxItemsError(context, expected_length)

            for item_member, item in zip(self.items, context.value):
                for error in item_member.get_errors(
                    item,
                    parent_context = context
                ):
                    yield error

    def translate_value(self, value, language = None, **kwargs):
        try:
            desc = []
            for item, member in zip(value, self.items):
                desc.append(member.translate_value(item))
            return u", ".join(desc)
        except:
            return Member.translate_value(
                self,
                value,
                language = language,
                **kwargs
            )

