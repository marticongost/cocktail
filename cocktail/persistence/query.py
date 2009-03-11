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
                    "Negative indexes not supported on query ranges: %d, %d"
                    % value
                )
            
            self.__range = value

    range = property(_get_range, _set_range, doc = """        
        Limits the set of matching instances to the given integer range. Ranges
        start counting from zero. Negative indexes or None values are not
        allowed.
        @type: (int, int) tuple
        """)

    # Execution
    #--------------------------------------------------------------------------    
    def execute(self, _sorted = True):
    
        base_collection = self.base_collection
        ordered = isinstance(base_collection, (list, tuple, ListWrapper))
        dataset = base_collection

        if self.__filters:
            dataset = self._apply_filters(dataset)

        if _sorted:            
            if ordered and not self.__order:
                dataset = [item for item in base_collection if item in dataset]
            else:
                dataset = self._apply_order(dataset)

            dataset = self._apply_range(dataset)

        return dataset

    def _apply_filters(self, dataset):
                
        for expr, custom_impl in self._get_execution_plan(self.__filters):

            if not isinstance(dataset, set):
                dataset = set(dataset)

            # As soon as the matching set is reduced to an empty set
            # there's no point in applying any further filter
            if not dataset:
                break
 
            # Default filter implementation. Used when no custom transformation
            # function is provided, or if the dataset has been reduced to a
            # single item (to spare the intersection between the results for
            # all remaining filters)
            if custom_impl is None or len(dataset) == 1:
                 dataset.intersection_update(
                    instance
                    for instance in dataset
                    if expr.eval(instance, SchemaObjectAccessor)
                )
            # Custom filter implementation
            else:
                dataset = custom_impl(dataset)

        return dataset

    def _get_execution_plan(self, filters):
        """Create an optimized execution plan for the given set of filters."""
        return [
            (filter, resolution[1])
            for resolution, filter
            in sorted((expr.resolve_filter(), expr) for expr in filters)
        ]
    
    def _get_expression_index(self, expr, member = None):

        # Expressions can override normal indexes and supply their own
        if isinstance(expr, Member):
            index = self._get_member_index(expr)
        else:
            index = expr.index
                
        # Otherwise, just use the one provided by the evaluated member
        if index is None and member is not None:
            index = self._get_member_index(member)

        return index

    def _get_member_index(self, member):

        if member.indexed:
            if member.primary:
                return self.__type.index
            else:
                return member.index

        return None
    
    def _apply_order(self, dataset):
 
        order = self.__order

        # Force a default order on queries that don't specify one, but request
        # a dataset range
        if not order:
            if self.range:
                order = [self.__type.primary_member.positive()]
            else:
                return dataset 
        
        # Optimized case: single indexed member, or a member that is both
        # required and unique followed by other members
        expr = order[0].operands[0]
        index = self._get_expression_index(expr)
        
        if index is not None and (
            len(order) == 1
            or (isinstance(expr, Member) and expr.unique and expr.required)
        ):            
            if not isinstance(dataset, set):
                dataset = set(dataset)

            dataset = [item
                       for item in index.itervalues()
                       if item in dataset]

            if isinstance(order[0], expressions.NegativeExpression):
                dataset.reverse()

            return dataset

        # Optimized case: indexes available for all involved criteria
        indexes = []
        
        for criteria in order:            
            index = self._get_expression_index(criteria.operands[0])            
            if index is None:
                break            
            reversed = isinstance(criteria, expressions.NegativeExpression)
            indexes.append((index, reversed))            
        else:
            ranks = {}
            
            def add_rank(item, rank):
                item_ranks = ranks.get(item)
                if item_ranks is None:
                    item_ranks = []
                    ranks[item] = item_ranks
                item_ranks.append(rank)

            if not isinstance(dataset, set):
                dataset = set(dataset)

            for index, reversed in indexes:
                
                if isinstance(index, Index):
                    for i, key in enumerate(index):
                        if reversed:
                            i = -i
                        for item in index[key]:
                            if item in dataset:
                                add_rank(item, i)
                else:
                    for i, item in enumerate(index.itervalues()):
                        if item in dataset:
                            if reversed:
                                i = -i                        
                            add_rank(item, i)

            return sorted(dataset, key = ranks.__getitem__)

        # Proceed with the brute force approach
        if not isinstance(dataset, list):
            dataset = list(dataset)

        order_expressions = []
        descending = []
        
        for expr in order:
            order_expressions.append(expr.operands[0])
            descending.append(isinstance(expr, expressions.NegativeExpression))

        entries = [
            (
                item,
                tuple(
                    expr.eval(item, SchemaObjectAccessor)
                    for expr in order_expressions
                )
            )
            for item in dataset
        ]

        def compare(entry_a, entry_b):
            
            values_a = entry_a[1]
            values_b = entry_b[1]

            for expr, desc, value_a, value_b in zip(
                order_expressions,
                descending,
                values_a,
                values_b
            ):            
                if desc:
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

        entries.sort(cmp = compare)
        return [entry[0] for entry in entries]

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

# Custom expression resolution
#------------------------------------------------------------------------------
def _get_filter_info(filter):

    if isinstance(filter, Member):
        member = filter
        index = member.index
    else:
        member = filter.operands[0] \
            if filter.operands and isinstance(filter.operands[0], Member) \
            else None
    
        index = member.index if member is not None else None

        if index is None:
            index = filter.index

    unique = not isinstance(index, Index)
    return member, index, unique

def _expression_resolution(self):
    return ((0, 0), None)
    
expressions.Expression.resolve_filter = _expression_resolution

def _equal_resolution(self):

    member, index, unique = _get_filter_info(self)     

    if index is None:
        return ((0, -1), None)

    elif unique:
        order = (-2, -1)
        def impl(dataset):
            value = member.get_index_value(self.operands[1].value)
            match = index.get(value)
                        
            if match is None:
                return set()
            else:
                return set([match])
    else:
        order = (-1, -1)
        def impl(dataset):
            value = member.get_index_value(self.operands[1].value)
            subset = index[value]
            dataset.intersection_update(subset)
            return dataset
    
    return (order, impl)

expressions.EqualExpression.resolve_filter = _equal_resolution

def _not_equal_resolution(self):

    member, index, unique = _get_filter_info(self)     

    if index is None:
        return ((0, 0), None)
    elif unique:
        order = (-2, 0)
        def impl(dataset):
            value = member.get_index_value(self.operands[1].value)
            index_value = index.get(value)
            if index_value is not None:
                dataset.discard(index_value)
            return dataset
    else:
        order = (-1, -1)
        def impl(dataset):
            subset = index[value]
            dataset.difference_update(subset)
            return dataset
    
    return (order, impl)

expressions.NotEqualExpression.resolve_filter = _not_equal_resolution

def _greater_resolution(self):

    member, index, unique = _get_filter_info(self)

    if index is None:
        return ((0, 0), None)
    else:
        exclude_end = isinstance(self, expressions.GreaterExpression)
        def impl(dataset):
            value = member.get_index_value(self.operands[1].value)
            subset = index.values(
                min = value,
                excludemin = exclude_end
            )
            dataset.intersection_update(subset)

        return ((-2 if unique else -1, 0), impl)

expressions.GreaterExpression.resolve_filter = _greater_resolution
expressions.GreaterEqualExpression.resolve_filter = _greater_resolution

def _lower_resolution(self):

    member, index, unique = _get_filter_info(self)

    if index is None:
        return ((0, 0), None)
    else:
        exclude_end = isinstance(self, expressions.LowerExpression)
        def impl(dataset):
            value = member.get_index_value(self.operands[1].value)
            subset = index.values(
                max = value,
                excludemax = exclude_end
            )
            dataset.intersection_update(subset)

        return ((-2 if unique else -1, 0), impl)

expressions.LowerExpression.resolve_filter = _lower_resolution
expressions.LowerEqualExpression.resolve_filter = _lower_resolution

def _inclusion_resolution(self):

    if self.operands and self.operands[0] is expressions.Self:
        
        subset = self.operands[1].eval(None)

        if not isinstance(subset, (set, frozenset)):
            subset = set(subset)

        def impl(dataset):
            dataset.intersection_update(subset)
            return dataset
        
        return ((-3, 0), impl)
    else:
        return ((0, 0), None)

expressions.InclusionExpression.resolve_filter = _inclusion_resolution

def _exclusion_resolution(self):

    if self.operands and self.operands[0] is expressions.Self:
        
        subset = self.operands[1].eval(None)

        if not isinstance(subset, (set, frozenset)):
            subset = set(subset)

        def impl(dataset):
            dataset.difference_update(subset)
            return dataset
        
        return ((-3, 0), impl)
    else:
        return ((0, 0), None)

expressions.ExclusionExpression.resolve_filter = _exclusion_resolution

# TODO: Provide an index aware custom implementation for StartsWithExpression
expressions.StartsWithExpression.resolve_filter = lambda self: ((0, -1), None)
expressions.EndsWithExpression.resolve_filter = lambda self: ((0, -1), None)
expressions.ContainsExpression.resolve_filter = lambda self: ((0, -2), None)
expressions.MatchExpression.resolve_filter = lambda self: ((0, -3), None)
expressions.SearchExpression.resolve_filter = lambda self: ((0, -4), None)

def _has_resolution(self):

    index = self.relation.index
    unique = not isinstance(index, Index)

    if index is None:
        return ((1, 0), None)
    else:
        def impl(dataset):

            related_subset = self.relation.related_type.select(self.filters)
            
            if related_subset:
                
                subset = set()

                if unique:
                    for item in related_subset:
                        referer = index.get(item.id)
                        if referer is not None:
                            subset.add(referer)
                else:
                    for item in related_subset:
                        referers = index[item.id]
                        if referers:
                            subset.update(referers)

                dataset.intersection_update(subset)
                return dataset
            else:
                return set()
                
        return ((0, -1), impl)

expressions.HasExpression.resolve_filter = _has_resolution


