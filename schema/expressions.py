#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import operator

class Expression(object):
    
    op = None
    operands = ()

    def __init__(self, *operands):
        self.operands = tuple(self.wrap(operand) for operand in operands)

    def eval(self, context, get_value = operator.getitem):
        return self.op(*[operand.eval(context, get_value)
                         for operand in self.operands])

    @classmethod
    def wrap(cls, expr):
        if isinstance(expr, Expression):
            return expr
        else:
            return Constant(expr)

    def __eq__(self, expr):
        return EqualExpression(self, expr)

    def __ne__(self, expr):
        return NotEqualExpression(self, expr)

    def __gt__(self, expr):
        return GreaterExpression(self, expr)

    def __ge__(self, expr):
        return GreaterEqualExpression(self, expr)

    def __lt__(self, expr):
        return LowerExpression(self, expr)

    def __le__(self, expr):
        return LowerEqualExpression(self, expr)

    def __add__(self, expr):
        return AddExpression(self, expr)

    def __sub__(self, expr):
        return SubtractExpression(self, expr)

    def __mul__(self, expr):
        return ProductExpression(self, expr)

    def __div__(self, expr):
        return DivisionExpression(self, expr)

    def and_(self, expr):
        return AndExpression(self, expr)

    def or_(self, expr):
        return OrExpression(self, expr)

    def not_(self):
        return NotExpression(self)

    def __neg__(self):
        return NegativeExpression(self)

    def __pos__(self):
        return PositiveExpression(self)

    def startswith(self, expr):
        return StartsWithExpression(self, expr)

    def endswith(self, expr):
        return EndsWithExpression(self, expr)

    def __contains__(self, expr):
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

    def eval(self, context, get_value = operator.getitem):
        return self.value


class Variable(Expression):

    def __init__(self, name):
        self.name = name

    def eval(self, context, get_value = operator.getitem):
        return get_value(context, self.name)


class CustomExpression(Expression):

    def __init__(self, expression):
        self.expression = expression

    def eval(self, context, get_value = operator.getitem):
        return self.expression(context)


class EqualExpression(Expression):
    op = operator.eq


class NotEqualExpression(Expression):
    op = operator.ne


class GreaterExpression(Expression):
    op = operator.gt


class GreaterEqualExpression(Expression):
    op = operator.ge


class LowerExpression(Expression):
    op = operator.lt


class LowerEqualExpression(Expression):
    op = operator.le


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


class StartsWithExpression(Expression):
    
    def op(self, a, b):
        return a.startswith(b)


class EndsWithExpression(Expression):

    def op(self, a, b):
        return a.endswith(b)


class ContainsExpression(Expression):
    op = operator.contains    


class MatchExpression(Expression):

    def op(self, a, b):
        if isinstance(b, basestring):
            b = re.compile(b)

        return b.match(a)


class SearchExpression(Expression):

    def op(self, a, b):
        if isinstance(b, basestring):
            b = re.compile(b)

        return b.search(a)
 

class TranslationExpression(Expression):

    def eval(self, context, get_value = operator.getitem):
        return context.get(self.operands[0], self.operands[1].value)

