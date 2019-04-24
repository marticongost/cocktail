"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .member import Member


class Enumeration(Member):

    def get_possible_values(self, context = None):

        if self.type:
            return set(self.type.__members__.values())

        return super().get_possible_values(context)

    def to_json_value(self, value, **options):
        return value and value.name

    def from_json_value(self, value, **options):
        return (
            value
            and self.type
            and getattr(self.type, value, value)
        )

