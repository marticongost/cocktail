#-*- coding: utf-8 -*-
u"""
Provides a member that handles textual values.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""
import re
from cocktail.schema.member import Member
from cocktail.schema.exceptions import MinLengthError, \
                                       MaxLengthError, \
                                       FormatError

class String(Member):
    """A member that handles textual values.
    
    @ivar min: A constraint that establishes the minimum number of characters
        accepted by the member. If set to a value other than None, setting the
        member to a string shorter than this limit will trigger a
        L{MinLengthError<exceptions.MinLengthError>} validation error.
    @type min: int
    
    @ivar max: A constraint that limits the maximum number of characters
        accepted by the member. If set to a value other than None, setting the
        member to a string longer than this limit will trigger a
        L{MaxLengthError<exceptions.MaxLengthError>} validation error.
    @type max: int
    """

    type = basestring
    min = None
    max = None
    _format = None

    def __init__(self, *args, **kwargs):
        Member.__init__(self, *args, **kwargs)
        self.add_validation(String.string_validation_rule)

    def _get_format(self):
        return self._format

    def _set_format(self, value):

        # Normalize strings to regular expressions
        if isinstance(value, basestring):
            value = re.compile(value)

        self._format = value

    format = property(_get_format, _set_format, doc = """
        A constraint that enforces a certain format uppon values. Formats are
        described using regular expressions. When set to a value other than
        None, setting the member to a string that doesn't comply with the
        required format will trigger a L{FormatError<exceptions.FormatError>}
        validation error.
        @type: regular expression or str
        """)

    def _set_length(self, value):
        self.min = value
        self.max = value

    length = property(None, _set_length, doc = """
        A convenience write-only property that sets both L{min} and L{max} at
        once.
        @type: int
        """)

    def string_validation_rule(self, value, context):
        """Validation rule for string values. Checks the L{min}, L{max} and
        L{format} constraints."""

        if value is not None:

            # Min length
            min = self.resolve_constraint(self.min, context)

            if min is not None and len(value) < min:
                yield MinLengthError(self, value, context, min)

            # Max length
            else:
                max = self.resolve_constraint(self.max, context)

                if max is not None and len(value) > max:
                    yield MaxLengthError(self, value, context, max)

            # Format
            format = self.resolve_constraint(self.format, context)
            
            if format is not None and not format.search(value):
                yield FormatError(self, value, context, format)

    # Special treatment for the 'format' property (regular expressions don't
    # support deep copying)
    _special_copy_keys = Member._special_copy_keys | set(["_format"])

    def __deepcopy__(self, memo):
        copy = Member.__deepcopy__(self, memo)
        copy.format = self.format
        return copy

