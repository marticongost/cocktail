#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from unittest import TestCase


class ComparisonTestCase(TestCase):

    def test_eval_greater(self):
        from cocktail.schema.expressions import GreaterExpression
        assert GreaterExpression(3, 2).eval({})
        assert not GreaterExpression(2, 2).eval({})
        assert not GreaterExpression(1, 2).eval({})
        assert GreaterExpression(1, None).eval({})
        assert not GreaterExpression(None, None).eval({})
        assert not GreaterExpression(None, 3).eval({})

    def test_eval_greater_equal(self):
        from cocktail.schema.expressions import GreaterEqualExpression
        assert GreaterEqualExpression(3, 2).eval({})
        assert GreaterEqualExpression(2, 2).eval({})
        assert not GreaterEqualExpression(1, 2).eval({})
        assert GreaterEqualExpression(1, None).eval({})
        assert GreaterEqualExpression(None, None).eval({})
        assert not GreaterEqualExpression(None, 3).eval({})

    def test_eval_lower(self):
        from cocktail.schema.expressions import LowerExpression
        assert not LowerExpression(3, 2).eval({})
        assert not LowerExpression(2, 2).eval({})
        assert LowerExpression(1, 2).eval({})
        assert not LowerExpression(1, None).eval({})
        assert not LowerExpression(None, None).eval({})
        assert LowerExpression(None, 3).eval({})

    def test_eval_lower_equal(self):
        from cocktail.schema.expressions import LowerEqualExpression        
        assert not LowerEqualExpression(3, 2).eval({})
        assert LowerEqualExpression(2, 2).eval({})
        assert LowerEqualExpression(1, 2).eval({})
        assert not LowerEqualExpression(1, None).eval({})
        assert LowerEqualExpression(None, None).eval({})
        assert LowerEqualExpression(None, 3).eval({})

