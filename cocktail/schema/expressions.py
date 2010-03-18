#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import re
import operator
from cocktail.translations import translations
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

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join(repr(operand) for operand in self.operands)
        )

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

    def one_of(self, expr):
        return InclusionExpression(self, expr)
    
    def not_one_of(self, expr):
        return ExclusionExpression(self, expr)

    def startswith(self, expr):
        return StartsWithExpression(self, expr)

    def endswith(self, expr):
        return EndsWithExpression(self, expr)

    def contains(self, expr):
        return ContainsExpression(self, expr)

    def match(self, expr):
        return MatchExpression(self, expr)

    def search(self, expr):
        return SearchExpression(self, expr)

    def translated_into(self, language):
        return TranslationExpression(self, language)

    def between(self,
        i = None,
        j = None,
        excludemin = False,
        excludemax = True):
        
        min_operator = (
            GreaterExpression
            if excludemin
            else GreaterEqualExpression
        )

        max_operator = (
            LowerExpression
            if excludemax
            else LowerEqualExpression
        )

        if i is not None and j is not None:
            expr = min_operator(self, i).and_(max_operator(self, j))
        elif i is not None:
            expr = min_operator(self, i)            
        elif j is not None:
            expr = max_operator(self, j)
        else:
            expr = Constant(True)

        if excludemin and i is None:
            expr = expr.and_(self.not_equal(None))

        return expr

    def isinstance(self, expr):
        return IsInstanceExpression(Self, expr)

    def is_not_instance(self, expr):
        return IsNotInstanceExpression(Self, expr)

    def descends_from(self, expr, relation, include_self = True):
        return DescendsFromExpression(
            self, expr, relation, include_self = include_self
        )


class Constant(Expression):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Constant(%r)" % self.value

    def eval(self, context = None, accessor = None):
        return self.value

    def __translate__(self, language, **kwargs):
        if self.value is None:
            return u"Ø"
        else:
            return translations(self.value, language, **kwargs) \
                or unicode(self.value)


class Variable(Expression):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Variable(%r)" % self.value

    def eval(self, context, accessor = None):
        return (accessor or get_accessor(context)) \
               .get(context, self.name, None)


class SelfExpression(Expression):

    def eval(self, context, accessor = None):
        return context

Self = SelfExpression()


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
            if a is not None:
                a = normalize(a)
            if not self._invariable_normalized and b is not None:
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
        if a is None:
            return False
        elif b is None:
            return True
        else:
            return a > b


class GreaterEqualExpression(NormalizableExpression):
    
    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        if a is None:
            return b is None
        elif b is None:
            return True
        else:
            return a >= b


class LowerExpression(NormalizableExpression):

    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        if b is None:
            return False
        elif a is None:
            return True
        else:
            return a < b


class LowerEqualExpression(NormalizableExpression):

    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        if b is None:
            return a is None
        elif a is None:
            return True
        else:
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


class GlobalSearchExpression(Expression):

    def __init__(self, search, languages):
        Expression.__init__(self)
        self.search_query = search
        self.search_words = set(normalize(search).split())
        self.languages = languages

    def eval(self, context, accessor = None):        
        text = u" ".join(context.get_searchable_text(self.languages))
        text = normalize(text)
        return all((word in text) for word in self.search_words)


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


class InclusionExpression(Expression):

    by_key = False
    
    def op(self, a, b):
        if self.by_key:
            return a.id in b
        else:
            return a in b


class ExclusionExpression(Expression):
 
    by_key = False

    def op(self, a, b):
        if self.by_key:
            return a.id not in b
        else:
            return a not in b


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


class AnyExpression(Expression):

    def __init__(self, relation, filters = None):
        self.relation = relation
        self.filters = filters

    def eval(self, context, accessor = None):
        
        value = (accessor or get_accessor(context)).get(context, self.relation)

        if value:
            if self.filters:
                for item in value:
                    for filter in self.filters:
                        if not filter.eval(item, accessor):
                            break
                    else:
                        return True
            else:
                return True

        return False


class AllExpression(Expression):

    def __init__(self, relation, filters):
        self.relation = relation
        self.filters = filters

    def eval(self, context, accessor = None):
        
        value = (accessor or get_accessor(context)).get(context, self.relation)

        if value:            
            for item in value:
                for filter in self.filters:
                    if not filter.eval(item, accessor):
                        return False

        return True


class HasExpression(Expression):

    def __init__(self, relation, filters = None):
        self.relation = relation
        self.filters = filters

    def eval(self, context, accessor = None):
        
        value = (accessor or get_accessor(context)).get(context, self.relation)

        if value:
            return all(filter.eval(value, accessor) for filter in self.filters)

        return False


class RangeIntersectionExpression(Expression):

    excludemin = False
    excludemax = True

    def __init__(self, a, b, c, d, excludemin = False, excludemax = True):
        Expression.__init__(self, a, b, c, d)
        self.excludemin = excludemin
        self.excludemax = excludemax

    def op(self, a, b, c, d):
        min_operator = (
            GreaterExpression
            if self.excludemin
            else GreaterEqualExpression
        )

        max_operator = (
            LowerExpression
            if self.excludemax
            else LowerEqualExpression
        )
        
        return (
            (d is None or max_operator(a, d).eval({}))
            and (b is None or min_operator(b, c).eval({}))
        )


class IsInstanceExpression(Expression):

    is_inherited = True

    def __init__(self, a, b, is_inherited = True):
        if isinstance(b, type):
            b = Constant(b)
        Expression.__init__(self, a, b)
        self.is_inherited = is_inherited

    def op(self, a, b):
        if self.is_inherited:
            return isinstance(a, b)
        else:
            if isinstance(b, tuple):
                return a.__class__ in b
            else:
                return a.__class__ == b


class IsNotInstanceExpression(IsInstanceExpression):

    def op(self, a, b):
        return not IsInstanceExpression.op(self, a, b)


class DescendsFromExpression(Expression):

    # The relation parameter always is the children relation.
    def __init__(self, a, b, relation, include_self = True):
        Expression.__init__(self, a, b)
        self.relation = relation
        self.include_self = include_self


    def op(self, a, b):

        if self.relation.bidirectional and (
            not self.relation.related_end._many or not self.relation._many
        ):
            def find(root, target, relation, include_self):

                if include_self and root == target:
                    return True

                item = root.get(relation)

                while item is not None:
                    if item is target:
                        return True
                    item = item.get(relation)

                return False

            if not self.relation.related_end._many:
                return find(a, b, self.relation.related_end, self.include_self)
            elif not self.relation._many:
                return find(b, a, self.relation, self.include_self)

        else:
            def find(root, target, relation, include_self):

                if include_self and root == target:
                    return True

                value = root.get(relation)

                if not value:
                    return False
                else:
                    if not relation._many:
                        value = [value]

                    if target in value:
                        return True
                    else:
                        for v in value:
                            result = find(v, target, relation, True)
                            if result:
                                return result

                        return False

            return find(b, a, self.relation, self.include_self)


