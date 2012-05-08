#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import re
import operator
from cocktail.translations import (
    translations,
    get_language,
    language_context
)
from cocktail.schema.accessors import get_accessor
from cocktail.stringutils import normalize


class Expression(object):
    
    op = None
    operands = ()
    
    def __init__(self, *operands):
        self.operands = tuple(self.wrap(operand) for operand in operands)

    def __eq__(self, other):
        return type(self) is type(other) and self.operands == other.operands

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

    def search(self,
        query,
        languages = None,
        logic = "and",
        partial_word_match = False
    ):
        return SearchExpression(
            self,
            query,
            languages = languages,
            logic = logic,
            partial_word_match = partial_word_match
        )

    def translated_into(self, language):
        return TranslationExpression(self, language)

    def between(self,
        i = None,
        j = None,
        exclude_min = False,
        exclude_max = True):
        
        min_operator = (
            GreaterExpression
            if exclude_min
            else GreaterEqualExpression
        )

        max_operator = (
            LowerExpression
            if exclude_max
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

        if exclude_min and i is None:
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

    def __eq__(self, other):
        return type(self) is type(other) and self.value == other.value
        
    def __repr__(self):
        return "Constant(%s)" % repr(self.value)

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
        if a is None or b is None:
            return False
        return a.startswith(b)


class EndsWithExpression(NormalizableExpression):

    def op(self, a, b):
        a, b = self.normalize_operands(a, b)
        if a is None or b is None:
            return False
        return a.endswith(b)


class GlobalSearchExpression(Expression):

    def __init__(self, search, languages = None, logic = "and"):
        Expression.__init__(self)
        self.search_query = search
        self.search_words = set(normalize(search).split())
        
        if languages is None:
            languages = [get_language()]
        else:
            languages = list(languages)

        if None not in languages:
            languages.append(None)
        
        self.languages = languages
        self.logic = logic

    def eval(self, context, accessor = None):        
        text = u" ".join(context.get_searchable_text(self.languages))
        text = normalize(text)
        return any((word in text) for word in self.search_words)


class SearchExpression(Expression):

    __query = None
    __tokens = frozenset()
    __logic = "and"

    def __init__(self,
        subject,
        query,
        languages = None,
        logic = "and",
        partial_word_match = False
    ):
        Expression.__init__(self, subject, query)
        self.subject = subject
        self.query = query
        self.languages = languages
        self.__logic = logic
        self.partial_word_match = partial_word_match

    def _get_query(self):
        return self._query

    def _set_query(self, query):
        
        if not isinstance(query, basestring):
            raise TypeError(
                'SearchExpression.query must be set to a string, '
                'got %r instead'
                % query
            )

        self.__query = query
        self.__tokens = frozenset(self.tokenize(query))

    query = property(_get_query, _set_query)

    @property
    def tokens(self):
        return self.__tokens

    def tokenize(self, text):
        return (self.normalize(token) for token in text.split())

    def normalize(self, word):
        return normalize(word)

    def eval(self, context, accessor = None):
        
        languages = self.languages
        if languages is None:
            languages = [get_language()]

        added_language_neutral_text = False
        text_body = []

        for language in languages:
            with language_context(language):
                lang_text = self.subject.eval(context, accessor)
                get_searchable_text = getattr(
                    lang_text, "get_searchable_text", None
                )
                if get_searchable_text is not None:
                    if not added_language_neutral_text:
                        text_body.extend(get_searchable_text([None]))
                        added_language_neutral_text = True
                    text_body.extend(get_searchable_text([language]))
                else:
                    text_body.append(lang_text)

        # Accept partial word matches (ie. a text containing "John Sanderson"
        # would match a query for "sand").
        if self.partial_word_match:
            searchable_text = normalize(u" ".join(text_body))
            operator = all if self.logic == "and" else any
            return operator(
                (token in searchable_text) 
                for token in self.__tokens
            )
        
        # Match full words only (ie. a text containing "John Sanderson" would
        # not match a query for "sand", but "John Sanderson walked across the
        # sand" would).
        else:
            subject_tokens = self.tokenize(u" ".join(text_body))

            if self.logic == "and":
                return not (self.__tokens - frozenset(subject_tokens))
            else:
                return any(token in self.__tokens for token in subject_tokens)

    def _get_logic(self):
        return self.__logic

    def _set_logic(self, logic):
        if logic not in ("and", "or"):
            raise ValueError(
                "Unknown logic for SearchExpression: "
                "expected 'and' or 'or', got %r instead"
                % logic
            )
        
        self.__logic = logic

    logic = property(_get_logic, _set_logic, doc = """
        Gets or sets the behavior of the search expression when given a query
        containing multiple words. Should be a string, indicating "and"
        (matches must contain all the given words) or "or" (matches must
        contain one or more of the given words).
        """)


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

    exclude_min = False
    exclude_max = True

    def __init__(self, a, b, c, d, exclude_min = False, exclude_max = True):
        Expression.__init__(self, a, b, c, d)
        self.exclude_min = exclude_min
        self.exclude_max = exclude_max

    def op(self, a, b, c, d):
        min_operator = (
            GreaterExpression
            if self.exclude_min
            else GreaterEqualExpression
        )

        max_operator = (
            LowerExpression
            if self.exclude_max
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


