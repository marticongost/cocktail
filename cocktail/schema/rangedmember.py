#-*- coding: utf-8 -*-
u"""
Provides a base class for all schema members that can restrict their values to
certain ranges.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2008
"""
from cocktail.schema.exceptions import MinValueError, MaxValueError

class RangedMember(object):
    """A mixin class, used as a base for members that can constrain their
    values to a certain range (numbers, dates, etc).

    @ivar min: Sets the minimum value accepted by the member. If set to a value
        other than None, values below this limit will produce a
        L{MinValueError<exceptions.MinValueError>} during validation.

    @ivar max: Sets the maximum value accepted by the member. If set to a value
        other than None, values above this limit will produce a
        L{MaxValueError<exceptions.MaxValueError>} during validation.
    """
    min = None
    max = None

    def _range_validation(self, context):
        """Validation rule for value ranges. Checks the L{min} and L{max}
        constraints."""

        if context.value is not None:

            type = self.resolve_constraint(self.type, context)

            if type is None or isinstance(context.value, type):

                min = self.resolve_constraint(self.min, context)

                if min is not None and context.value < min:
                    yield MinValueError(context, min)
                else:
                    max = self.resolve_constraint(self.max, context)

                    if max is not None and context.value > max:
                        yield MaxValueError(context, max)

