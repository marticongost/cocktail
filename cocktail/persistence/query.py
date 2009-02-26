#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from itertools import chain
from cocktail.modeling import getter, ListWrapper
from cocktail.schema import Member, expressions, SchemaObjectAccessor
from cocktail.persistence.index import Index

inherit = object()


class Query(object):
    """A query over a set of persistent objects."""

    _indexable_expressions = set([
        expressions.EqualExpression,
        expressions.NotEqualExpression,
        expressions.GreaterExpression,
        expressions.GreaterEqualExpression,
        expressions.LowerExpression,
        expressions.LowerEqualExpression
    ])

    _expression_speed = {
        expressions.EqualExpression: -1,
        expressions.StartsWithExpression: 1,
        expressions.EndsWithExpression: 1,
        expressions.ContainsExpression: 1,
        expressions.MatchExpression: 2,
        expressions.SearchExpression: 2,
        expressions.CustomExpression: 2
    }

    def __init__(self,
        type,
        filters = None,
        order = None,
        range = None,
        base_collection = None):

        self.__type = type
        self.__filters = None
        self.__order = None
        self.__base_collection = None

        self.filters = filters or []
        self.order = order or []
        self.range = range
        self.base_collection = base_collection

    @getter
    def type(self):
        """The base type of the instances returned by the query.
        @type: L{PersistentObject<cocktail.persistence.persistentobject.PersistentObject>}
            subclass
        """
        return self.__type

    def _get_base_collection(self):
        if self.__base_collection is None:
            return self.type.index.itervalues()
        else:
            return self.__base_collection
    
    def _set_base_collection(self, value):

        if value is None and not self.type.indexed:
            raise TypeError("An indexed persistent class is required")

        self.__base_collection = value

    base_collection = property(_get_base_collection, _set_base_collection,
        doc = """The base set of persistent objects that the query operates on.
        When set to None, the query works with the full set of instances for
        the selected type.
        @type: L{PersistentObject<cocktail.persistence.PersistentObject>}
        """)

    def _get_filters(self):
        return self.__filters
    
    def _set_filters(self, value):
        
        if value is None:
            self.__filters = []
        else:
            if isinstance(value, expressions.Expression):
                self.__filters = [value]
            elif isinstance(value, dict):
                self.__filters = [
                    self.type[k].equal(v) for k, v in value.iteritems()
                ]
            else:
                self.__filters = list(value)

    filters = property(_get_filters, _set_filters, doc = """
        An optional set of constraints that all instances produced by the query
        must fulfill. All expressions are joined using a logical 'and'
        expression.
        @type filters: L{Expression<cocktail.schema.expressions.Expression>}
            list
        """)
    
    def add_filter(self, filter):
        if self.filters is None:
            self.filters = [filter]
        else:
            self.filters.append(filter)

    def _get_order(self):
        return self.__order or []

    def _set_order(self, value):

        if value is None:
            self.__order = []
        else:
            if isinstance(value, (basestring, expressions.Expression)):
                value = value,

            order = []

            for criteria in value:
                order.append(self._normalize_order_criteria(criteria))

            self.__order = order

    order = property(_get_order, _set_order, doc = """            
        Specifies the order in which instances are returned. Can take both
        single and multiple sorting criteria. Criteria can be specified using
        member names or references to L{Member<cocktail.schema.member.Member>}
        objects.
        
        When specified using a string, an optional '+' or '-' prefix can be
        used to choose between ascending (default) and descending order,
        respectively. When using member references, the same can be
        accomplished by wrapping the reference inside a
        L{PositiveExpression<cocktail.schema.expressions.PositiveExpression>}
        or a L{NegativeExpression<cocktail.schema.expressions.NegativeExpression>}.

        @type: str,
            str collection,
            L{Expression<cocktail.schema.expressions.Expression>},
            L{Expression<cocktail.schema.expressions.Expression>} collection
        """)

    def add_order(self, criteria):
        self.__order.append(self._normalize_order_criteria(criteria))

    def _normalize_order_criteria(self, criteria):
        
        if isinstance(criteria, basestring):
            if not criteria:
                raise ValueError(
                    "An empty string is not a valid query filter"
                )
            
            wrapper = None

            if criteria[0] == "+":
                criteria = criteria[1:]
                wrapper = expressions.PositiveExpression
            elif criteria[0] == "-":
                criteria = criteria[1:]
                wrapper = expressions.NegativeExpression

            criteria = self.type[criteria]

            if wrapper:
                criteria = wrapper(criteria)
        
        elif not isinstance(criteria, expressions.Expression):
            raise TypeError(
                "Query.order expected a string or Expression, got "
                "%s instead" % criteria
            )

        if not isinstance(criteria,
            (expressions.PositiveExpression,
            expressions.NegativeExpression)
        ):
            criteria = expressions.PositiveExpression(criteria)

        return criteria

    def _get_range(self):
        return self.__range

    def _set_range(self, value):

        if value is None:
            self.__range = value
        else:
            if not isinstance(value, tuple) \
            or len(value) != 2 \
            or not isinstance(value[0], int) \
            or not isinstance(value[1], int):
                raise TypeError("Invalid query range: %s" % value)
            
            if value[0] < 0 or value[1] < 0:
                raise ValueError(
                    "Negative indices not supported on query ranges: %d, %d"
                    % value
                )
            
            self.__range = value

    range = property(_get_range, _set_range, doc = """        
        Limits the set of matching instances to the given integer range. Ranges
        start counting from zero. Negative indices or None values are not
        allowed.
        @type: (int, int) tuple
        """)

    def execute(self, _sorted = True):
    
        base_collection = self.base_collection
        ordered = isinstance(base_collection, (list, tuple, ListWrapper))
        dataset = base_collection

        if self.__filters:
            dataset = self._apply_filters(dataset)

        if _sorted:
            if self.__order:
                dataset = self._apply_order(dataset)
            elif ordered:
                dataset = [item for item in base_collection if item in dataset]

            dataset = self._apply_range(dataset)

        return dataset

    def _apply_filters(self, dataset):
        
        single_match = False
        dataset = set(dataset)
        
        for order, filter, member, index, is_unique \
        in self._get_execution_plan(self.__filters):
            
            # Apply the filter using an index
            if index is not None and not single_match:

                value = member.get_index_value(filter.operands[1].value)
                
                # Equal
                if isinstance(filter, expressions.EqualExpression):

                    if is_unique:
                        match = index.get(value)
                        
                        if match:
                            dataset = set([match])
                            
                            # Special case: after an 'identity' filter is
                            # resolved (an equality check against a unique
                            # index), all further filters will ignore
                            # indices and use direct logical matching
                            # instead (should be faster)
                            single_match = True
                        else:
                            dataset = set()
                    else:
                        subset = index[value]
                        dataset.intersection_update(subset)
                
                # Different
                elif isinstance(filter, expressions.NotEqualExpression):
                    
                    if is_unique:
                        index_value = index.get(value)
                        if index_value is not None:
                            dataset.discard(index_value)
                    else:
                        subset = index[value]
                        dataset.difference_update(subset) 

                # Greater
                elif isinstance(filter, (
                    expressions.GreaterExpression,
                    expressions.GreaterEqualExpression
                )):
                    subset = index.values(
                        min = value,
                        excludemin = isinstance(filter,
                            expressions.GreaterExpression)
                    )
                    dataset.intersection_update(subset)
            
                # Lower
                elif isinstance(filter, (
                    expressions.LowerExpression,
                    expressions.LowerEqualExpression
                )):
                    subset = index.values(
                        max = value,
                        excludemax = isinstance(filter,
                            expressions.LowerExpression)
                    )
                    dataset.intersection_update(subset)
                else:
                    raise TypeError(
                        "Can't match %s against an index" % filter)
            else:
                # Intersection
                if isinstance(filter, expressions.InclusionExpression) \
                and filter.operands[0] is expressions.Self:
                    subset = filter.operands[1].eval(None)
                    dataset.intersection_update(subset)
                    
                # Exclusion
                elif isinstance(filter, expressions.ExclusionExpression) \
                and filter.operands[0] is expressions.Self:
                    subset = filter.operands[1].eval(None)
                    dataset.difference_update(subset)
                
                # Brute force matching
                else:
                    dataset.intersection_update(
                        instance
                        for instance in dataset
                        if filter.eval(instance, SchemaObjectAccessor))

            # As soon as the matching set is reduced to an empty set
            # there's no point in applying any further filter
            if not dataset:
                break

        return dataset

    def _get_filter_member(self, filter):
        return filter.operands[0] \
            if filter.operands and isinstance(filter.operands[0], Member) \
            else None

    def _get_execution_plan(self, filters):

        # Create an optimized execution plan
        execution_plan = []

        for filter in filters:
            
            member = self._get_filter_member(filter)
            expr_speed = self._expression_speed.get(filter.__class__, 0)
            index = None
            index_speed = 2
            is_unique = None
            
            if member:
                if filter.__class__ in self._indexable_expressions:
                    index = self._get_expression_index(filter, member)
                
                if index is not None:
                    is_unique = self._index_is_unique(index)
                
                    if is_unique:
                        index_speed = 0
                    else:
                        index_speed = 1
                            
            order = (index_speed, expr_speed)
            execution_plan.append((order, filter, member, index, is_unique))

        execution_plan.sort()
        return execution_plan

    def _get_expression_index(self, filter, member):

        # Expressions can override normal indices and supply their own
        index = filter.index

        # Otherwise, just use the one provided by the evaluated member
        if index is None and member.indexed:
            if member.primary:
                index = self.__type.index
            else:
                index = member.index

        return index
    
    def _index_is_unique(self, index):
        return not isinstance(index, Index)

    def _apply_order(self, dataset):
 
        # TODO: Use indices!

        order = self.__order

        if not order:
            if self.range:
                order = [self.__type.primary_member.positive()]
            else:
                return dataset 

        if not isinstance(dataset, list):
            dataset = list(dataset)

        cmp_sequence = [
            (
                expr.operands[0],
                isinstance(expr, expressions.NegativeExpression)
            )
            for expr in order
        ]

        def compare(a, b):
 
            for expr, descending in cmp_sequence:
                value_a = expr.eval(a, SchemaObjectAccessor)
                value_b = expr.eval(b, SchemaObjectAccessor)

                if descending:
                    value_a, value_b = value_b, value_a

                if (value_a is None and value_b is None) \
                or value_a == value_b:
                    pass
                elif value_a is None:
                    return -1
                elif value_b is None:
                    return 1
                elif value_a < value_b:
                    return -1
                elif value_a > value_b:
                    return 1

            return 0

        dataset.sort(cmp = compare)

        return dataset

    def _apply_range(self, dataset):

        r = self.range
        
        if dataset and r:
            dataset = dataset[r[0]:r[1]]

        return dataset

    def __iter__(self):
        for instance in self.execute():
            yield instance

    def __len__(self):
        
        if self.filters:
            return len(self.execute(_sorted = False))
        else:
            if self.__base_collection is None:
                return len(self.type.index)
            else:
                return len(self.__base_collection)
    
    def __notzero__(self):
        # TODO: Could be optimized to look for just one match on each filter
        return bool(self.execute(_sorted = False))

    def __contains__(self, item):
        # TODO: This too could be optimized
        return bool(self.select(item.__class__.primary_member.equal(item.id)))

    def __getitem__(self, index):
        
        # Retrieve a slice
        if isinstance(index, slice):
            if index.step is not None and index.step != 1:
                raise ValueError("Can't retrieve a query slice using a step "
                        "different than 1")
            return self.select(range = (index.start, index.stop))

        # Retrieve a single item
        else:
            return self.execute()[index]

    def select(self,
        filters = inherit,
        order = inherit,
        range = inherit):
        
        child_query = self.__class__(
            self.__type,
            self.filters if filters is inherit else filters,
            self.order if order is inherit else order,
            self.range if range is inherit else range,
            self.__base_collection)

        return child_query

