#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2008
"""
from decimal import Decimal
from cocktail.schema.member import Member
from cocktail.schema.rangedmember import RangedMember


class Number(Member, RangedMember):
    """Base class for all members that handle numeric values."""

    def __init__(self, **kwargs):
        Member.__init__(self, **kwargs)
        RangedMember.__init__(self)        


class Integer(Number):
    """A numeric field limited integer values."""
    type = int


class Float(Number):
    """A numeric field limited to float values."""
    type = float


class Decimal(Number):
    """A numeric field limited to decimal values."""
    type = Decimal


