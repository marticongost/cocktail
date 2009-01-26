#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import re
import operator
from cocktail.schema.accessors import get_accessor

normalization_map = {}

for repl, chars in (
    (u"a", u"áàäâ"),
    (u"e", u"éèëê"),
    (u"i", u"íìïî"),
    (u"o", u"óòöô"),
    (u"u", u"úùüû")
):
    for c in chars:
        normalization_map[ord(c)] = ord(repl)

def normalize(string):
    string = string.lower()
    
    if isinstance(string, unicode):
        string = string.translate(normalization_map)

    return string


class Expression(object):
    
    op = None
    operands = ()
    
    def __init__(self, *operands):
        self.operands = tuple(self.wrap(operand) for operand in operands)

    def eval(self, context = None, accessor = None):
        return self.op(*[operand.eval(context, accessor)
                         for operand in self.operands])

    @classmethod
    def wrap(cls, expr):
        if isinstance(expr, Expression):
            return expr
        else:
            return Constant(expr)

    def equal(self, expr):
        return EqualExpression(self, expr)

    def not_equal(self, expr):
        return NotEqualExpression(self, expr)

    def greater(self, expr):
        return GreaterExpression(self, expr)

    def greater_equal(self, expr):
        return GreaterEqualExpression(self, expr)

    def lower(self, expr):
        return LowerExpression(self, expr)

    def lower_equal(self, expr):
        return LowerEqualExpression(self, expr)

    def plus(self, expr):
        return AddExpression(self, expr)

    def minus(self, expr):
        return SubtractExpression(self, expr)

    def multiplied_by(self, expr):
        return ProductExpression(self, expr)

    def divided_by(self, expr):
        return DivisionExpression(self, expr)

    def and_(self, expr):
        return AndExpression(self, expr)

    def or_(self, expr):
        return OrExpression(self, expr)

    def not_(self):
        return NotExpression(self)

    def negative(self):
        return NegativeExpression(self)

    def positive(self):
        return PositiveExpression(self)

    def startswith(self, expr):
        return StartsWithExpression(self, expr)

    def endswith(self, expr):
        return EndsWithExpression(self, expr)

    def contains(self, expr):
        return ContainsExpression(expr, self)

    def match(self, expr):
        return MatchExpression(self, expr)

    def search(self, expr):
        return SearchExpression(self, expr)

    def translated_into(self, language):
        return TranslationExpression(self, language)


class Constant(Expression):

    def __init__(self, value):
        self.value = value

    def eval(self, context = None, accessor = None):
        return self.value


class Variable(Expression):

    def __init__(self, name):
        self.name = name

    def eval(self, context, accessor = None):
        return (accessor or get_accessor(context)) \
               .get(context, self.name, None)


class CustomExpression(Expression):

    def __init__(self, expression):
        self.expression = expression

    def eval(self, context = None, accessor = None):
        return self.expression(context)


class NormalizableExpression(Expression):

    normalized_strings = False
    _invariable_normalized = False
    
    def normalize_operands(self, a, b):

        if self.normalized_strings:
            a = normalize(a)
            if not self._invariable_normalized:
                b = normalize(b)

        return a, b

    def normalize_invariable(self):
        self.operands = (
            self.operands[0],
            Constant(normalize(self.operands[1].eval()))
        )


class EqualExpression(NormalizableExpression):
    
    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        return a == b


class NotEqualExpression(NormalizableExpression):
    
    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        return a != b


class GreaterExpression(NormalizableExpression):
    
    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        return a > b


class GreaterEqualExpression(NormalizableExpression):
    
    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        return a >= b


class LowerExpression(NormalizableExpression):

    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        return a < b


class LowerEqualExpression(NormalizableExpression):

    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        return a <= b


class StartsWithExpression(NormalizableExpression):
    
    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        return a.startswith(b)


class EndsWithExpression(NormalizableExpression):

    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        return a.endswith(b)


class SearchExpression(NormalizableExpression):

    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        return all((word in a) for word in b.split())


class AddExpression(Expression):
    op = operator.add


class SubtractExpression(Expression):
    op = operator.sub


class ProductExpression(Expression):
    op = operator.mul


class DivisionExpression(Expression):
    op = operator.div


class AndExpression(Expression):
    
    def op(self, a, b):
        return a and b


class OrExpression(Expression):

    def op(self, a, b):
        return a or b


class NotExpression(Expression):
    op = operator.not_


class NegativeExpression(Expression):
    op = operator.neg


class PositiveExpression(Expression):
    op = operator.pos


class ContainsExpression(Expression):
    op = operator.contains    


class MatchExpression(Expression):

    def op(self, a, b):
        if isinstance(b, basestring):
            b = re.compile(b)

        return b.search(a)


class TranslationExpression(Expression):

    def eval(self, context, accessor = None):
        return context.get(self.operands[0], self.operands[1].value)

