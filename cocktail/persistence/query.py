#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from itertools import chain
from cocktail.modeling import getter
from cocktail.persistence import PersistentClass
from cocktail.schema import Member, expressions, SchemaObjectAccessor

inherit = object()


class Query(object):

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
        expressions.SearchExpression: 2
    }

    def __init__(self,
        type,
        filters = None,
        order = None,
        range = None,
        base_collection = None):

        if base_collection is None:

            if not isinstance(type, PersistentClass) \
            or not type.indexed:
                raise TypeError("An indexed persistent class is required")

            base_collection = type.index.values()

        if filters is not None and not isinstance(filters, list):
            filters = [filters]

        self.__type = type
        self.__base_collection = base_collection
        self.__parent = None
        self.filters = filters
        self.order = order
        self.range = range

    @getter
    def type(self):
        return self.__type

    @getter
    def parent(self):
        return self.__parent

    def execute(self, _sorted = True):
     
        subset = self.__apply_filters()

        if _sorted:
            subset = self.__apply_order(subset)
            subset = self.__apply_range(subset)

        return subset

    def __apply_filters(self):

        dataset = self.__base_collection
        single_match = False

        for order, filter in self._get_execution_plan(self.filters):
            
            member = self._get_filter_member(filter)

            # Apply the filter using an index
            if member and member.indexed \
            and filter in self._indexable_expressions \
            and not single_match:

                value = filter.operands[1].value

                if member.primary:
                    index = self.__type.index
                else:
                    index = member.index

                # Equal
                if isinstance(filter, expressions.EqualExpression):

                    if member.unique:
                        match = index.get(value)
                        
                        if match:
                            subset = set([match])
                            
                            # Special case: after an 'identity' filter is
                            # resolved (an equality check against a unique
                            # index), all further filters will ignore
                            # indices and use direct logical matching
                            # instead (should be faster)
                            single_match = True
                        else:
                            subset = set()
                    else:
                        subset = index[value]
                
                # Different
                elif isinstance(filter, expressions.NotEqualExpression):
                    lower = index.values(
                        max = value, excludemax = True)
                    higher = index.values(
                        min = value, excludemin = True)
                    subset = chain(lower, higher)

                # Greater
                elif isinstance(filter, (
                    expressions.GreaterExpression,
                    expressions.GreaterEqualExpression
                )):
                    subset = index.values(
                        min = value,
                        excludemax = isinstance(filter,
                            expressions.GreaterExpression)
                    )
            
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

                else:
                    raise TypeError(
                        "Can't match %s against an index" % filter)

                # Add matches together
                if subset:
                    if not isinstance(dataset, set):
                        dataset = set(dataset)

                    dataset = dataset.intersection(subset)
                else:
                    dataset = set()

            # Brute force matching
            else:
                dataset = [instance
                          for instance in dataset
                          if filter.eval(instance, SchemaObjectAccessor)]

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

            if member and member.indexed \
            and filter.__class__ in self._indexable_expressions:
                if member.unique:
                    indexing = 0
                else:
                    indexing = 1
            else:
                indexing = 2
            
            order = (indexing, expr_speed)
            execution_plan.append((order, filter))

        execution_plan.sort()
        return execution_plan

    def __apply_order(self, subset):
 
        # TODO: Should optimize the usual case where sorting is done on a
        # single, indexed member without any filter in place

        order = self.order

        if not order:            
            if self.range:
                order = [self.__type.primary_member.positive()]
            else:
                return subset

        if not isinstance(subset, list):
            subset = list(subset)

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

        subset.sort(cmp = compare)

        return subset

    def __apply_range(self, subset):

        range = self.range
        
        if range:
            subset = subset[range[0]:range[1]]

        return subset

    def __iter__(self):
        for instance in self.execute():
            yield instance

    def __len__(self):
        results = self.execute(_sorted = False)
        return len(results)
    
    def __notzero__(self):
        # TODO: Could be optimized to quit as soon as the first match is found
        return bool(self.execute(_sorted = False))

    def __contains__(self, item):
        return bool(self.select_by(id = item.id))

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

        child_query.__parent = self
        return child_query

    def select_by(self, **kwargs):
        for key, value in kwargs.itervalues():
            member = getattr(self.__type, key)
            self.add_filter(key == value)

    def add_filter(self, filter):
        if self.filters is None:
            self.filters = [filter]
        else:
            self.filters.append(filter)

    def add_order(self, criteria):
        
        if isinstance(criteria, basestring):
            member = self.type[criteria]
            criteria = expressions.PositiveExpression(member)
        
        elif isinstance(criteria, Member):
            criteria = expressions.PositiveExpression(criteria)
        
        if self.order is None:
            self.order = []

        self.order.append(criteria)

