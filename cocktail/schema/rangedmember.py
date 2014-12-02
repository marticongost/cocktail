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

    def __init__(self):
        self.add_validation(RangedMember.range_validation_rule)

    def range_validation_rule(self, value, context):
        """Validation rule for value ranges. Checks the L{min} and L{max}
        constraints."""

        if value is not None:

            type = self.resolve_constraint(self.type, context)

            if type is None or isinstance(value, type):

                min = self.resolve_constraint(self.min, context)

                if min is not None and value < min:
                    yield MinValueError(self, value, context, min)
                else:
                    max = self.resolve_constraint(self.max, context)

                    if max is not None and value > max:
                        yield MaxValueError(self, value, context, max)

