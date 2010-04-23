#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from time import time
from itertools import chain
from cocktail.styled import styled
from cocktail.modeling import getter, ListWrapper
from cocktail.translations import get_language
from cocktail.schema import Member, expressions, SchemaObjectAccessor
from cocktail.schema.io import export_file
from cocktail.schema.expressions import TranslationExpression
from cocktail.persistence.index import Index

query_style = lambda t: styled(t.ljust(80), "white", "blue")
query_attrib_style = lambda k, v: (
    " " * 4
    + styled((k + ":").ljust(15), style = "bold")
    + str(v)
)
query_cached_style = lambda t: styled(" " * 4 + t, "white", "green")
query_phase_style = lambda t: " " * 4 + styled(t, style = "underline")
query_eval_style = (
    lambda expr: " " * 4 + styled("Eval:", "magenta") + str(expr)
)
query_initial_dataset_style = (
    lambda dataset:
        " " * 4 + "Initial dataset: "
        + styled(len(dataset), style = "bold")
)
query_resolve_style = (
    lambda expr: " " * 4 + styled("Resolve:", "bright_green") + str(expr)
)
query_results_style = (
    lambda n: " " * 4 + styled(n, style = "bold")
)
query_timing_style = lambda s: " " * 4 + ("%.4fs" % s)

inherit = object()

class Query(object):
    """A query over a set of persistent objects."""

    verbose = False

    def __init__(self,
        type,
        filters = None,
        order = None,
        range = None,
        base_collection = None,
        cached = True,
        verbose = None):

        self.__type = type
        self.__filters = None
        self.__order = None
        self.__base_collection = None

        self.__cached_results = None
        self.__cached_results_sorted = False

        self.filters = filters or []
        self.order = order or []
        self.range = range
        self.base_collection = base_collection
        self.cached = cached

        if verbose is not None:
            self.verbose = verbose

    def __repr__(self):
        return (
            "Query("
            "type = %s, "
            "filters = %r, "
            "order = %r, "
            "range = %r, "
            "cached = %r)" % (
                self.__type.full_name,
                self.__filters,
                self.__order,
                self.__range,
                self.cached
            )
        )

    def discard_results(self):
        self.__cached_results = None
        self.__cached_results_sorted = False

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

        self.discard_results()
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
        
        self.discard_results()

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
        
        self.discard_results()

        if self.filters is None:
            self.filters = [filter]
        else:
            self.filters.append(filter)

    def _get_order(self):
        return self.__order or []

    def _set_order(self, value):

        self.discard_results()

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
        self.discard_results()
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

        if self.verbose:
            print query_style("Query")
            print query_attrib_style("type", self.type.full_name)

            if self.filters:
                print query_attrib_style("filters", self.filters)

            if self.order:
                print query_attrib_style("order", self.order)

            if self.range:
                print query_attrib_style("range", self.range)
            
        # Try to make use of cached results
        if self.cached and self.__cached_results is not None:
            dataset = self.__cached_results
            
            if self.verbose:
                print query_cached_style("cached")

        # New data set
        else:
            # Object universe
            if self.__base_collection is None:
                dataset = self.type.keys
            else:
                dataset = (obj.id for obj in self.__base_collection)

            # Apply filters
            if self.verbose:
                start = time()
                print query_phase_style("Applying filters")

            if self.__filters:
                dataset = self._apply_filters(dataset)

            if self.verbose:
                print query_timing_style(time() - start)

        # Apply order
        if _sorted and not (self.cached and self.__cached_results_sorted):

            if self.verbose:
                start = time()
                print query_phase_style("Applying order")
            
            # Preserve ordering when selecting items from a custom ordered
            # collection
            if not self.__order and isinstance(
                self.__base_collection,
                (list, tuple, ListWrapper)
            ):
                dataset = [obj.id
                           for obj in self.__base_collection
                           if obj.id in dataset]
            else:
                dataset = self._apply_order(dataset)

            if self.verbose:
                print query_timing_style(time() - start)

        # Store results for further requests
        if self.cached:
            self.__cached_results = dataset
            self.__cached_results_sorted = _sorted
        
        # Apply ranges
        if _sorted:
            if self.verbose:
                start = time()
                print query_phase_style("Applying range")
            
            dataset = self._apply_range(dataset)

            if self.verbose:
                print query_timing_style(time() - start)

        if self.verbose:
            print

        return dataset

    def _apply_filters(self, dataset):
 
        type_index = self.type.index
        
        if self.verbose:
            print query_initial_dataset_style(dataset)

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

                if self.verbose:
                    print query_eval_style(expr)

                dataset.intersection_update(
                    id
                    for id in dataset
                    if expr.eval(type_index[id], SchemaObjectAccessor)
                )
                
            # Custom filter implementation
            else:
                
                if self.verbose:
                    print query_resolve_style(expr)

                dataset = custom_impl(dataset)

            if self.verbose:
                print query_results_style(len(dataset))

        return dataset

    def _get_execution_plan(self, filters):
        """Create an optimized execution plan for the given set of filters."""

        plan = []
        And = expressions.AndExpression

        for filter in filters:
            # Flatten regular AND expressions
            if isinstance(filter, And):
                for operand in filter.operands:
                    plan.append((operand.resolve_filter(self), operand))
            else:
                plan.append((filter.resolve_filter(self), filter))

        plan.sort()

        for resolution, filter in plan:
            yield (filter, resolution[1])
    
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
 
        order = []

        # Wrap the translated members into a TranslationExpression
        for criteria in self.__order:
            member = criteria.operands[0]
            if isinstance(member, Member) and member.translated:
                order.append(criteria.__class__(
                    member.translated_into(get_language())
                ))
            else:
                order.append(criteria)

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

        if isinstance(expr, TranslationExpression):
            language = expr.operands[1].eval(None)
            expr = expr.operands[0]

        index = self._get_expression_index(expr)

        if index is not None and (
            len(order) == 1
            or (isinstance(expr, Member) and expr.unique and expr.required)
        ):            
            if not isinstance(dataset, set):
                dataset = set(dataset)

            if isinstance(expr, Member) and expr.primary:
                sequence = index.iterkeys()
            else:
                if expr.translated:
                    sequence = (id
                                for key, id in index.iteritems()
                                if key[0] == language)
                else:
                    sequence = index.itervalues()

            dataset = [id
                       for id in sequence
                       if id in dataset]

            if isinstance(order[0], expressions.NegativeExpression):
                dataset.reverse()

            return dataset

        # Optimized case: indexes available for all involved criteria
        indexes = []
        
        for criteria in order:            
            expr = criteria.operands[0]

            if isinstance(expr, TranslationExpression):
                language = expr.operands[1].eval(None)
                expr = expr.operands[0]
            else:
                language = None

            index = self._get_expression_index(expr)
            if index is None:
                break            
            reversed = isinstance(criteria, expressions.NegativeExpression)
            indexes.append((expr, index, reversed, language))
        else:
            ranks = {}
            
            def add_rank(id, rank):
                item_ranks = ranks.get(id)
                if item_ranks is None:
                    item_ranks = []
                    ranks[id] = item_ranks
                item_ranks.append(rank)

            if not isinstance(dataset, set):
                dataset = set(dataset)

            for expr, index, reversed, language in indexes:
             
                if isinstance(index, Index):
                    for i, key in enumerate(index):
                        if reversed:
                            i = -i
                        if expr.translated and key[0] != language:
                            continue
                        for id in index[key]:
                            if id in dataset:
                                add_rank(id, i)
                else:                    
                    if isinstance(expr, Member) and expr.primary:
                        sequence = index.iterkeys()
                    else:
                        if expr.translated:
                            sequence = (id
                                for key, id in index.iteritems()
                                if key[0] == language)
                        else:
                            sequence = index.itervalues()

                    for i, id in enumerate(sequence):
                        if id in dataset:
                            if reversed:
                                i = -i                        
                            add_rank(id, i)

            return sorted(dataset, key = ranks.__getitem__)

        # Proceed with the brute force approach
        if not isinstance(dataset, list):
            dataset = list(dataset)

        order_expressions = []
        descending = []
        
        for expr in order:
            order_expressions.append(expr.operands[0])
            descending.append(isinstance(expr, expressions.NegativeExpression))

        type_index = self.type.index

        entries = []

        for id in dataset:
            sorting_values = []
            for expr in order_expressions:
                value = expr.eval(type_index[id], SchemaObjectAccessor)
                if hasattr(value, "get_ordering_key"):
                    value = value.get_ordering_key()
                sorting_values.append(value)
            entries.append([id, sorting_values])

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
        type_index = self.type.index
        for id in self.execute():
            yield type_index[id]
        
    def __len__(self):
        
        if self.filters:
            return len(self.execute(_sorted = False))
        else:
            if self.__base_collection is None:
                return len(self.type.keys)
            else:
                return len(self.__base_collection)
    
    def __notzero__(self):
        # TODO: Could be optimized to look for just one match on each filter
        return bool(self.execute(_sorted = False))

    def __contains__(self, item):
        # TODO: This too could be optimized
        return item.id in self.execute()

    def __getitem__(self, index):
        
        # Retrieve a slice
        if isinstance(index, slice):
            if index.step is not None and index.step != 1:
                raise ValueError("Can't retrieve a query slice using a step "
                        "different than 1")
            
            return self.select(range = (index.start, index.stop))

        # Retrieve a single item
        else:
            results = self.execute()
            return self.type.index[results[index]]

    def select(self,
        filters = inherit,
        order = inherit,
        range = inherit):
        
        child_query = self.__class__(
            self.__type,
            self.filters if filters is inherit else filters + self.filters,
            self.order if order is inherit else order,
            self.range if range is inherit else range,
            self.__base_collection)

        if filters is None:
            child_query.__cached_results = self.__cached_results
            child_query.__cached_results_sorted = order is None \
                and self.__cached_results_sorted

        return child_query

    def delete_items(self):
        """Delete all items matched by the query."""
        type_index = self.type.index
        for id in list(self.execute(_sorted = False)):
            item = type_index.get(id)
            if item is not None:
                item.delete()

    # Exportation
    #------------------------------------------------------------------------------
    def export_file(self, dest, mime_type = None, members = None, **kwargs):
        """Exports the query to a file"""
        export_file(self, dest, self.type, mime_type, members, **kwargs)
        


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

def _get_index_value(member, value):
    value = member.get_index_value(value)
    if member.translated:
        value = (get_language(), value)
    return value

def _expression_resolution(self, query):
    return ((0, 0), None)
    
expressions.Expression.resolve_filter = _expression_resolution

def _equal_resolution(self, query):

    member, index, unique = _get_filter_info(self)     

    if index is None:
        return ((0, -1), None)

    elif unique:
        order = (-2, -1)

        if member and member.primary:
            def impl(dataset):
                id = _get_index_value(member, self.operands[1].value)
                return set([id]) if id in dataset else set()
        else:
            def impl(dataset):
                value = _get_index_value(member, self.operands[1].value)
                match = index.get(value)
                            
                if match is None:
                    return set()
                else:
                    return set([match])
    else:
        order = (-1, -1)
        def impl(dataset):
            value = _get_index_value(member, self.operands[1].value)
            subset = index[value]
            dataset.intersection_update(subset)
            return dataset
    
    return (order, impl)

expressions.EqualExpression.resolve_filter = _equal_resolution

def _not_equal_resolution(self, query):

    member, index, unique = _get_filter_info(self)     

    if index is None:
        return ((0, 0), None)
    elif unique:
        order = (-2, 0)
        
        if member and member.primary:
            def impl(dataset):
                id = _get_index_value(member, self.operands[1].value)
                dataset.discard(id)
                return dataset
        else:
            def impl(dataset):
                value = _get_index_value(member, self.operands[1].value)
                index_value = index.get(value)
                if index_value is not None:
                    dataset.discard(index_value)
                return dataset
    else:
        order = (-1, -1)
        def impl(dataset):
            value = _get_index_value(member, self.operands[1].value)
            subset = index[value]
            dataset.difference_update(subset)
            return dataset
    
    return (order, impl)

expressions.NotEqualExpression.resolve_filter = _not_equal_resolution

def _greater_resolution(self, query):

    member, index, unique = _get_filter_info(self)

    if index is None:
        return ((0, 0), None)
    else:
        exclude_end = isinstance(self, expressions.GreaterExpression)
        
        def impl(dataset):
            value = _get_index_value(member, self.operands[1].value)
            method = index.keys if member and member.primary else index.values
            subset = method(min = value, excludemin = exclude_end)
            dataset.intersection_update(subset)
            return dataset

        return ((-2 if unique else -1, 0), impl)

expressions.GreaterExpression.resolve_filter = _greater_resolution
expressions.GreaterEqualExpression.resolve_filter = _greater_resolution

def _lower_resolution(self, query):

    member, index, unique = _get_filter_info(self)

    if index is None:
        return ((0, 0), None)
    else:
        exclude_end = isinstance(self, expressions.LowerExpression)
        def impl(dataset):
            value = _get_index_value(member, self.operands[1].value)
            method = index.keys if member and member.primary else index.values
            subset = method(max = value, excludemax = exclude_end)
            dataset.intersection_update(subset)
            return dataset

        return ((-2 if unique else -1, 0), impl)

expressions.LowerExpression.resolve_filter = _lower_resolution
expressions.LowerEqualExpression.resolve_filter = _lower_resolution

def _inclusion_resolution(self, query):

    if self.operands and self.operands[0] is expressions.Self:
        
        subset = self.operands[1].eval(None)

        if not self.by_key:
            subset = set(item.id for item in subset)

        def impl(dataset):
            dataset.intersection_update(subset)
            return dataset
        
        return ((-3, 0), impl)
    else:
        return ((0, 0), None)

expressions.InclusionExpression.resolve_filter = _inclusion_resolution

def _exclusion_resolution(self, query):

    if self.operands and self.operands[0] is expressions.Self:
        
        subset = self.operands[1].eval(None)

        if not self.by_key:
            subset = set(item.id for item in subset)

        def impl(dataset):
            dataset.difference_update(subset)
            return dataset
        
        return ((-3, 0), impl)
    else:
        return ((0, 0), None)

expressions.ExclusionExpression.resolve_filter = _exclusion_resolution

# TODO: Provide an index aware custom implementation for StartsWithExpression
expressions.StartsWithExpression.resolve_filter = \
    lambda self, query: ((0, -1), None)

expressions.EndsWithExpression.resolve_filter = \
    lambda self, query: ((0, -1), None)

expressions.ContainsExpression.resolve_filter = \
    lambda self, query: ((0, -2), None)

expressions.MatchExpression.resolve_filter = \
    lambda self, query: ((0, -3), None)

expressions.SearchExpression.resolve_filter = \
    lambda self, query: ((0, -4), None)

def _has_resolution(self, query):

    index = self.relation.index
    unique = not isinstance(index, Index)

    if index is None:
        return ((1, 0), None)
    else:
        def impl(dataset):

            related_subset = \
                self.relation.related_type.select(self.filters).execute()
            
            if related_subset:
                
                subset = set()

                if unique:
                    for related_id in related_subset:
                        referer_id = index.get(related_id)
                        if referer_id is not None:
                            subset.add(referer_id)
                else:
                    for related_id in related_subset:
                        referers = index[related_id]
                        if referers:
                            subset.update(referers)

                dataset.intersection_update(subset)
                return dataset
            else:
                return set()
                
        return ((0, -1), impl)

expressions.HasExpression.resolve_filter = _has_resolution

def _range_intersection_resolution(self, query):

    min_member = (
        self.operands[0]
        if isinstance(self.operands[0], Member)
        else None
    )

    max_member = (
        self.operands[1]
        if isinstance(self.operands[1], Member)
        else None
    )

    if self.index:
        min_index, max_index = self.index
    else:
        min_index = None if min_member is None else min_member.index
        max_index = None if max_member is None else max_member.index
    
    # One or both fields not indexed
    if min_index is None or max_index is None:
        order = (0, 0)
        impl = None
    else:
        def impl(dataset):
            min_value = self.operands[2].value
            if min_member:
                min_value = _get_index_value(min_member, min_value)

            max_value = self.operands[3].value
            if max_member:
                max_value = _get_index_value(max_member, max_value)          
            
            min_method = (
                min_index.keys
                if min_member and min_member.primary
                else min_index.values
            )

            max_method = (
                max_index.keys
                if max_member and max_member.primary
                else max_index.values
            )

            subset = set(max_method(max = None, excludemax = False))
            subset.update(
                max_method(min = min_value, excludemin = self.excludemin)
            )

            if max_value is not None:
                subset.intersection_update(
                    min_method(max = max_value, excludemax = self.excludemax)
                )
            
            dataset.intersection_update(subset)
            return dataset

        # One or both fields have non-unique indexes
        if isinstance(min_index, Index) or isinstance(max_index, Index):
            order = (-1, 0)
        # Both fields have unique indexes
        else:
            order = (-2, 0)
    
    return (order, impl)


expressions.RangeIntersectionExpression.resolve_filter = \
    _range_intersection_resolution

def _isinstance_subset(expression):

    subset = set()

    if isinstance(expression.operands[1], expressions.Constant):
        operand = expression.operands[1].eval()
    else:
        operand = expression.operands[1]

    if isinstance(operand, (tuple, list)):
        models = operand
    else:
        models = list()
        models.append(operand)

    for cls in models:
        if expression.is_inherited:
            subset.update(cls.keys)
        else:
            children = cls.derived_schemas(recursive = False)
            children_subset = set()
            for child in children:
                children_subset.update(child.keys)
            subset.update(set(cls.keys).difference(children_subset))

    return subset

def _isinstance_resolution(self, query):
    # TODO: Implement the resolution for the queries that its first operand is
    #   a Reference

    if self.operands and self.operands[0] is expressions.Self:

        subset = _isinstance_subset(self)

        def impl(dataset):
            dataset.intersection_update(subset)
            return dataset
        
        return ((-3, 0), impl)
    else:
        return ((0, 0), None)

expressions.IsInstanceExpression.resolve_filter = _isinstance_resolution

def _is_not_instance_resolution(self, query):
    # TODO: Implement the resolution for the queries that its first operand is
    #   a Reference

    if self.operands and self.operands[0] is expressions.Self:
        
        subset = _isinstance_subset(self)

        def impl(dataset):
            dataset.difference_update(subset)
            return dataset
        
        return ((-3, 0), impl)
    else:
        return ((0, 0), None)

expressions.IsNotInstanceExpression.resolve_filter = _is_not_instance_resolution

def _descends_from_resolution(self, query):

    if self.operands[0] is expressions.Self:

        def impl(dataset):
            subset = set()
            root = self.operands[1].eval(None)
            relation = self.relation

            if relation._many:
                def descend(item, include_self):
                    if include_self:
                        subset.add(item.id)
                    children = item.get(relation)
                    if children:                
                        for child in children:
                            descend(child, True)
                descend(root, self.include_self)
            else:
                item = root if self.include_self else root.get(relation)

                while item is not None:
                    subset.add(item.id)
                    item = item.get(relation)
        
            dataset.intersection_update(subset)
            return dataset
        
        return ((-3, 0), impl)
    
    else:
        return ((0, 0), None)

expressions.DescendsFromExpression.resolve_filter = _descends_from_resolution

