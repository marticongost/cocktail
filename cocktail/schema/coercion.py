"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import enum


class Coercion(enum.Enum):
    """An enumeration that controls the behavior of schema coercion.

    Schema coercion is implemented by the `cocktail.schema.Member.coerce`
    method, and it allows to enforce a schema validation rules on a given
    data set, rejecting or altering parts of it to conform to the schema.

    .. attribute:: NONE

        Applies no validation. Invalid data is left as is.

    .. attribute:: SET_NONE

        Invalid members discard their value, replacing it with 'None'.

    .. attribute:: SET_DEFAULT

        Invalid members discard tehir value, replacing it with their default
        value.

    .. attribute:: FAIL_IMMEDIATELY

        As soon as an invalid member is found a suitable
        `cocktail.schema.exceptions.ValidationError` exception is raised.

    .. attribute:: FAIL

        If any validation errors are found, collect them into a
        `cocktail.schema.ErrorList` object and raise a
        `cocktail.schema.exceptions.CoercionError` exception.
    """
    NONE = enum.auto()
    SET_NONE = enum.auto()
    SET_DEFAULT = enum.auto()
    FAIL_IMMEDIATELY = enum.auto()
    FAIL = enum.auto()

