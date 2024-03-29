#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from typing import Iterable
from time import time
from warnings import warn
from itertools import chain, islice
from collections import deque
from BTrees.IIBTree import IIBTree
from BTrees.OIBTree import OIBTree
from BTrees.IOBTree import IOTreeSet, IOSet
from BTrees.OOBTree import OOTreeSet, OOSet
from cocktail.styled import styled
from cocktail.modeling import ListWrapper
from cocktail.stringutils import normalize
from cocktail.translations import (
    translations,
    get_language,
    require_language,
    words
)
from cocktail.schema import (
    Member,
    Collection,
    expressions,
    SchemaObjectAccessor,
    RelationMember
)
from cocktail.schema.expressions import TranslationExpression

inherit = object()

class Query(object):
    """A query over a set of persistent objects."""

    verbose = False
    watch = None

    styles = {
        "header":
            (lambda t: styled(t.ljust(80), "black", "slate_blue")),
        "nested_header":
            (lambda t: styled(t.ljust(76), "black", "violet")),
        "attrib":
            (lambda k, v:
                " " * 4
                + styled((k + ":").ljust(15), style = "bold")
                + str(v)
            ),
        "cached":
            (lambda t: " " * 4 + styled(t, "black", "bright_green")),
        "phase":
            (lambda t: " " * 4 + styled(t, "white", "black", "underline")),
        "eval":
            (lambda expr: " " * 4 + styled("Eval: ", "magenta") + str(expr)),
        "initial_dataset":
            (lambda dataset:
                " " * 4
                + "Initial dataset: "
                + styled(len(dataset), style = "bold")
            ),
        "resolve":
            (lambda expr:
                " " * 4
                + styled("Resolve: ", "bright_green")
                + str(expr)
            ),
        "results":
            (lambda n: " " * 4 + styled(n, style = "bold")),
        "watch_present":
            (lambda: " " * 4 + styled("Object found", "white", "green")),
        "watch_missing":
            (lambda: " " * 4 + styled("Object missing", "white", "magenta")),
        "timing":
            (lambda s: " " * 4 + ("%.4fs" % s))
    }

    def __init__(
        self,
        type,
        filters = None,
        order = None,
        range = None,
        base_collection = None,
        cached = True,
        verbose = None,
        description = None
    ):
        self.__type = type
        self.__filters = None
        self.__order = None
        self.__range = None
        self.__base_collection = None
        self.__cached_results = None
        self.__cached_results_sorted = False
        self.__cached_results_sliced = False
        self.__cached_length = None

        self.filters = filters or []
        self.order = order or []
        self.range = range
        self.base_collection = base_collection
        self.cached = cached
        self.nesting = 0
        self.description = description

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
        self.__cached_results_sliced = False
        self.__cached_length = None

    @property
    def type(self):
        """The base type of the instances returned by the query.
        @type: L{PersistentObject<cocktail.persistence.persistentobject.PersistentObject>}
            subclass
        """
        return self.__type

    def is_subset(self):
        return bool(self.__base_collection is not None or self.__filters)

    def _get_base_collection(self):
        if self.__base_collection is None:
            return list(self.type.index.values())
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
        self.__filters = self._normalize_filters(value)

    filters = property(_get_filters, _set_filters, doc = """
        An optional set of constraints that all instances produced by the query
        must fulfill. All expressions are joined using a logical 'and'
        expression.
        @type filters: L{Expression<cocktail.schema.expressions.Expression>}
            list
        """)

    def _normalize_filters(self, value):
        if value is None:
            return []
        elif isinstance(value, expressions.Expression):
            return [value]
        elif isinstance(value, dict):
            return [
                self.type[k].equal(v) for k, v in value.items()
            ]
        else:
            return list(value)

    def add_filter(self, filter):

        self.discard_results()

        if self.filters is None:
            self.filters = [filter]
        else:
            self.filters.append(filter)

    def extend_filters(self, filters):
        self.discard_results()
        self.__filters += self._normalize_filters(filters)

    def _get_order(self):
        return self.__order or []

    def _set_order(self, value):

        if value is None:
            order = []
        else:
            if isinstance(value, (str, expressions.Expression)):
                value = value,

            order = []

            for criteria in value:
                order.append(self._normalize_order_criteria(criteria))

        if order != self.__order:
            self.__cached_results_sorted = False
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
        self.__cached_results_sorted = False
        self.__order.append(self._normalize_order_criteria(criteria))

    def _normalize_order_criteria(self, criteria):

        if isinstance(criteria, str):
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

        if value is not None:
            if not isinstance(value, tuple) \
            or len(value) != 2 \
            or not isinstance(value[0], int) \
            or not isinstance(value[1], int):
                raise TypeError("Invalid query range: %s" % (value,))

            if value[0] < 0 or value[1] < 0:
                raise ValueError(
                    "Negative indexes not supported on query ranges: %d, %d"
                    % value
                )

        if value != self.__range:
            if self.__range is None:
                self.__cached_results_sliced = False
            else:
                self.discard_results()

            self.__range = value

    range = property(_get_range, _set_range, doc = """
        Limits the set of matching instances to the given integer range. Ranges
        start counting from zero. Negative indexes or None values are not
        allowed.
        @type: (int, int) tuple
        """)

    def _verbose_message(self, style, *args, **kwargs):
        print(" " * 4 * self.nesting + self.styles[style](*args, **kwargs))

    # Execution
    #--------------------------------------------------------------------------
    def execute(self, _sorted = True, _sliced = True):

        verbose = self.verbose or self.watch

        if verbose:

            if self.nesting:
                print()
                heading = "Nested query"
                heading_style = "nested_header"
            else:
                heading = "Query"
                heading_style = "header"

            if self.description:
                heading += ": " + self.description

            self._verbose_message(heading_style, heading)

            self._verbose_message("attrib", "type", self.type.full_name)

            if self.base_collection is not None:
                self._verbose_message(
                    "attrib",
                    "base coll.",
                    self._describe_collection(self.base_collection)
                )

            if self.filters:
                self._verbose_message("attrib", "filters", self.filters)

            if self.order:
                self._verbose_message("attrib", "order", self.order)

            if self.range:
                self._verbose_message("attrib", "range", self.range)

        # Try to make use of cached results
        if self.cached \
        and self.__cached_results is not None \
        and not (
            self.__cached_results_sliced
            and not self.__cached_results_sorted
            and _sorted
        ):
            dataset = self.__cached_results

            if verbose:
                self._verbose_message("cached", "cached")

        # New data set
        else:
            # Discard cached results
            self.discard_results()

            # Object universe
            if self.__base_collection is None:
                dataset = self.type.keys
            else:
                dataset = (obj.id for obj in self.__base_collection)

            # Apply filters
            if verbose:
                start = time()
                print()
                self._verbose_message("phase", "Applying filters")

            if self.__filters:
                dataset = self._apply_filters(dataset)

            if verbose:
                self._verbose_message("timing", time() - start)

        # Apply order
        if _sorted and not (self.cached and self.__cached_results_sorted):

            if verbose:
                start = time()
                print()
                self._verbose_message("phase", "Applying order")

            # Preserve ordering when selecting items from a custom ordered
            # collection
            if not self.__order and isinstance(
                self.__base_collection,
                ordered_collection_types
            ):
                subset = dataset

                if not isinstance(
                    subset,
                    fast_membership_test_sequence_types
                ):
                    subset = set(subset)

                dataset = (obj.id
                           for obj in self.__base_collection
                           if obj.id in subset)
            else:
                dataset = self._apply_order(dataset)

            if verbose:
                self._verbose_message("timing", time() - start)

        # Apply range
        if _sliced \
        and self.range \
        and not (self.cached and self.__cached_results_sliced):
            if verbose:
                start = time()
                print()
                self._verbose_message("phase", "Applying range")

            dataset = self._apply_range(dataset)

            if verbose:
                self._verbose_message("timing", time() - start)

        # Store results for further requests
        if self.cached:
            if not hasattr(dataset, "__len__"):
                dataset = list(dataset)
            self.__cached_results = dataset
            self.__cached_results_sorted = _sorted
            self.__cached_results_sliced = _sliced

        if verbose:
            print()

        return dataset

    def _describe_collection(
            self,
            collection: Iterable,
            max_elements: int = 10) -> str:

        if hasattr(collection, "__len__"):
            size = len(collection)

            if size <= max_elements:
                return repr(collection)
            else:
                return f"{collection.__class__.__name__} <{len(collection)}>"
        else:
            return collection.__class__.__name__

    def _apply_filters(self, dataset):

        type_index = self.type.index

        if self.watch:
            if not isinstance(self.watch, int):
                watched_id = self.watch.id
            else:
                watched_id = self.watch
        else:
            watched_id = None

        verbose = self.verbose or watched_id

        if verbose:
            if not isinstance(dataset, set):
                dataset = set(dataset)
            self._verbose_message("initial_dataset", dataset)

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

                if verbose:
                    self._verbose_message("eval", expr)

                dataset.intersection_update(
                    id
                    for id in dataset
                    if expr.eval(type_index[id], SchemaObjectAccessor)
                )

            # Custom filter implementation
            else:

                if verbose:
                    self._verbose_message("resolve", expr)

                dataset = custom_impl(dataset)

            if verbose:
                if watched_id:
                    if watched_id in dataset:
                        self._verbose_message("watch_present")
                    else:
                        self._verbose_message("watch_missing")

                self._verbose_message("results", len(dataset))

        return dataset

    def _get_execution_plan(self, filters):
        """Create an optimized execution plan for the given set of filters."""

        plan = []

        def _descend_expressions(expr):
            for child_expr in expr.iter_filter_expressions(self):
                if child_expr is expr:
                    yield expr
                else:
                    for descendant_expr in _descend_expressions(child_expr):
                        yield descendant_expr

        for filter in filters:
            for expr in _descend_expressions(filter):
                plan.append((expr.resolve_filter(self), expr))

        plan.sort(key = lambda resolution: resolution[0][0])

        for resolution, expr in plan:
            yield (expr, resolution[1])

    def _get_expression_index(self, expr, member = None):

        # Expressions can override normal indexes and supply their own
        if isinstance(expr, Member):
            index = self._get_member_index(expr)
        else:
            index = expr.index

        # Otherwise, just use the one provided by the evaluated member
        if index is None and member is not None:
            index = self._get_member_index(member)

        # Keyword arguments to pass to the index
        index_kw = getattr(expr, "index_kwargs", None) or {}

        return index, index_kw

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

        index, index_kw = self._get_expression_index(expr)

        if (
            index is not None
            and not index.accepts_repetition
            and (
                len(order) == 1
                or not index.accepts_multiple_values
            )
            # An index for a translated member can't use the fast path, because
            # it holds no values for objects that don't have a translation in
            # the active language
            and not getattr(expr, "translated", False)
        ):
            desc = isinstance(order[0], expressions.NegativeExpression)
            is_btree = isinstance(index, (IIBTree, OIBTree))

            # BTrees don't provide a means for efficient reverse iteration
            if not (desc and is_btree):

                if not isinstance(dataset, fast_membership_test_sequence_types):
                    dataset = set(dataset)

                if isinstance(expr, Member) and expr.primary:
                    sequence = index.keys(descending = desc, **index_kw)
                elif is_btree:
                    sequence = index.values(**index_kw)
                else:
                    sequence = index.values(descending = desc, **index_kw)

                ordered_dataset = (id
                           for id in sequence
                           if id in dataset)

                return ordered_dataset

        # General case: mix indexes and brute force sorting as needed
        sorting_keys = {}

        def add_sorting_key(c, item_id, key):
            item_keys = sorting_keys.get(item_id)

            if item_keys is None:
                sorting_keys[item_id] = item_keys = []

            count = len(item_keys)

            if count == c:
                item_keys.append(key)
            elif count == c + 1:
                pass # Keep the first value
            elif count < c:
                while len(item_keys) != c:
                    item_keys.append(None)
                item_keys.append(key)

        for c, criteria in enumerate(order):
            expr = criteria.operands[0]

            if isinstance(expr, TranslationExpression):
                language = expr.operands[1].eval(None)
                expr = expr.operands[0]
            else:
                language = None

            index, index_kw = self._get_expression_index(expr)
            desc = isinstance(criteria, expressions.NegativeExpression)

            # Sort using an index
            if index is not None:

                # Normalize the dataset to a set, to speed up lookups
                if not isinstance(dataset, set):
                    dataset = set(dataset)

                # Index with duplicates
                if index.accepts_multiple_values:
                    pos = 0
                    prev_key = None
                    for key, id in index.items(descending = desc, **index_kw):
                        # Skip entries in non-active languages
                        if not getattr(expr, "translated", False) \
                        or key[0] == language:
                            if id in dataset:
                                if key != prev_key:
                                    pos += 1
                                    prev_key = key

                                add_sorting_key(c, id, pos)

                # Index without duplicates
                else:
                    if isinstance(expr, Member) and expr.primary:
                        sequence = index.keys(descending = desc, **index_kw)
                    else:
                        if expr.translated:
                            sequence = (id
                                for key, id in index.items(descending = desc, **index_kw)
                                if key[0] == language)
                        else:
                            sequence = index.values(descending = desc, **index_kw)

                    for pos, id in enumerate(sequence):
                        if id in dataset:
                            add_sorting_key(c, id, pos)

            # Brute force
            else:
                if not isinstance(dataset, fast_membership_test_sequence_types):
                    dataset = set(dataset)

                for id in dataset:
                    instance = self.type.index[id]
                    value = expr.eval(instance, SchemaObjectAccessor)

                    # Allow related objects to specify their relative ordering
                    if hasattr(value, "get_ordering_key"):
                        value = value.get_ordering_key()

                    add_sorting_key(c, id, Comparator(value, desc))

        return sorted(
            dataset,
            key=(lambda value: sorting_keys.get(value, minus_infinite))
        )

    def _apply_range(self, dataset):

        r = self.range

        if dataset and r:
            dataset = islice(dataset, r[0], r[1])

        return dataset

    def __iter__(self):
        type_index = self.type.index
        for id in self.execute():
            yield type_index[id]

    def __len__(self):
        if self.cached:
            if self.__cached_length is None:
                self.__cached_length = len(self.execute(_sorted = False))

            return self.__cached_length
        else:
            return len(self.execute(_sorted = False))

    def __bool__(self):
        if self.cached and self.__cached_length is not None:
            return bool(self.__cached_length)

        for id in self.execute(_sorted = False, _sliced = False):
            return True

        return False

    def __contains__(self, item):
        if item is None:
            return False
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

            if hasattr(results, "__getitem__"):
                id = results[index]
            elif index < 0:
                queue = deque(results, -index)
                if len(queue) == -index:
                    id = queue[0]
                else:
                    return None
            else:
                for id in results:
                    if index == 0:
                        break
                    index -= 1
                else:
                    return None

            return self.type.index[id]

    def select(
        self,
        filters = inherit,
        order = inherit,
        range = inherit,
        verbose = inherit,
        description = inherit
    ):
        child_query = self.__class__(
            self.__type,
            self.filters
                if filters is inherit
                else self._normalize_filters(filters) + self.filters,
            self.order if order is inherit else order,
            self.range if range is inherit else range,
            self.__base_collection,
            verbose = self.verbose if verbose is inherit else verbose,
            description =
                self.description if description is inherit else description
        )

        if filters is inherit:
            child_query.__cached_results = self.__cached_results
            child_query.__cached_results_sorted = \
                self.__cached_results_sorted if order is inherit else False
            child_query.__cached_results_sliced = \
                self.__cached_results_sliced if range is inherit else False

        return child_query

    def delete_items(self):
        """Delete all items matched by the query."""
        type_index = self.type.index
        for id in list(self.execute(_sorted = False)):
            item = type_index.get(id)
            if item is not None:
                item.delete()


class MinusInfinite:

    def __eq__(self, other):
        return other is minus_infinite

    def __ne__(self, other):
        return other is not minus_infinite

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return other is minus_infinite

    def __lt__(self, other):
        return other is not minus_infinite

    def __le__(self, other):
        return True


minus_infinite = MinusInfinite()


class Comparator(object):
    """A wrapper for comparable values that takes into account None values and
    descending order.
    """

    def __init__(self, value, reversed = False):
        self.value = value
        self.reversed = reversed

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __gt__(self, other):

        a = self.value
        b = other.value

        if self.reversed:
            a, b = b, a

        return a is not None and (b is None or a > b)

    def __ge__(self, other):

        a = self.value
        b = other.value

        if self.reversed:
            a, b = b, a

        return a == b or (a is not None and (b is None or a > b))

    def __lt__(self, other):

        a = self.value
        b = other.value

        if self.reversed:
            a, b = b, a

        return b is not None and (a is None or a < b)

    def __le__(self, other):

        a = self.value
        b = other.value

        if self.reversed:
            a, b = b, a

        return a == b or (b is not None and (a is None or a < b))


# Custom expression resolution
#------------------------------------------------------------------------------
def _get_filter_info(filter):

    if isinstance(filter, Member):
        member = filter
        language = None
    elif (
        isinstance(filter.operands[0], TranslationExpression)
        and isinstance(filter.operands[0].operands[0], Member)
    ):
        member, language = filter.operands[0].operands
        language = language.eval()
    else:
        member = (
            filter.operands[0]
            if filter.operands and isinstance(filter.operands[0], Member)
            else None
        )
        language = None

    index = member and member.index or filter.index
    return member, index, language

def _get_index_value(member, value, language = None):
    value = member.get_index_value(value)
    if member.translated:
        value = (require_language(language), value)
    return value

def _iter_filter_expressions(self, query):
    yield self

expressions.Expression.iter_filter_expressions = _iter_filter_expressions

def _iter_and_filter_expressions(self, query):
    return self.operands

expressions.AndExpression.iter_filter_expressions = _iter_and_filter_expressions

def _expression_resolution(self, query):
    return ((0, 0), None)

expressions.Expression.resolve_filter = _expression_resolution

def _constant_resolution(self, query):

    def impl(dataset):
        return dataset if self.value else set()

    return ((-4, 0), impl)

expressions.Constant.resolve_filter = _constant_resolution

def _or_resolution(self, query):

    def impl(dataset):
        union = None

        for operand in self.operands:
            subquery = query.type.select(operand)
            subquery.verbose = query.verbose
            subquery.nesting = query.nesting + 1
            subquery.cached = False
            operand_results = subquery.execute()
            if union is None:
                union = operand_results
            else:
                union.update(operand_results)

        dataset.intersection_update(union)
        return dataset

    return ((0, 0), impl)

expressions.OrExpression.resolve_filter = _or_resolution

def _equal_resolution(self, query):

    member, index, language = _get_filter_info(self)

    if index is None:
        return ((0, -1), None)

    elif not index.accepts_multiple_values:
        order = (-2, -1)

        if member and member.primary:
            def impl(dataset):
                id = _get_index_value(
                    member,
                    self.operands[1].value,
                    language
                )
                return set([id]) if id in dataset else set()
        else:
            def impl(dataset):
                value = _get_index_value(
                    member,
                    self.operands[1].value,
                    language
                )
                match = index.get(value)
                if match is None:
                    return set()
                else:
                    return set([match])
    else:
        order = (-1, -1)
        def impl(dataset):
            value = _get_index_value(
                member,
                self.operands[1].value,
                language
            )
            dataset.intersection_update(index.values(key = value))
            return dataset

    return (order, impl)

expressions.EqualExpression.resolve_filter = _equal_resolution

def _not_equal_resolution(self, query):

    member, index, language = _get_filter_info(self)

    if index is None:
        return ((0, 0), None)
    elif not index.accepts_multiple_values:
        order = (-2, 0)

        if member and member.primary:
            def impl(dataset):
                id = _get_index_value(
                    member,
                    self.operands[1].value,
                    language
                )
                dataset.discard(id)
                return dataset
        else:
            def impl(dataset):
                value = _get_index_value(
                    member,
                    self.operands[1].value,
                    language
                )
                index_value = index.get(value)
                if index_value is not None:
                    dataset.discard(index_value)
                return dataset
    else:
        order = (-1, -1)
        def impl(dataset):
            value = _get_index_value(member, self.operands[1].value)
            dataset.difference_update(index.values(key = value))
            return dataset

    return (order, impl)

expressions.NotEqualExpression.resolve_filter = _not_equal_resolution

def _greater_resolution(self, query):

    member, index, language = _get_filter_info(self)

    if index is None:
        return ((0, 0), None)
    else:
        exclude_end = isinstance(self, expressions.GreaterExpression)

        def impl(dataset):
            value = _get_index_value(member, self.operands[1].value, language)
            method = index.keys if member and member.primary else index.values
            subset = method(min = value, exclude_min = exclude_end)
            dataset.intersection_update(subset)
            return dataset

        return ((-1 if index.accepts_multiple_values else -2, 0), impl)

expressions.GreaterExpression.resolve_filter = _greater_resolution
expressions.GreaterEqualExpression.resolve_filter = _greater_resolution

def _lower_resolution(self, query):

    member, index, language = _get_filter_info(self)

    if index is None:
        return ((0, 0), None)
    else:
        exclude_end = isinstance(self, expressions.LowerExpression)
        def impl(dataset):
            value = _get_index_value(member, self.operands[1].value, language)
            method = index.keys if member and member.primary else index.values
            subset = method(max = value, exclude_max = exclude_end)
            dataset.intersection_update(subset)
            return dataset

        return ((-1 if index.accepts_multiple_values else -2, 0), impl)

expressions.LowerExpression.resolve_filter = _lower_resolution
expressions.LowerEqualExpression.resolve_filter = _lower_resolution

def ids_from_subset(subset, is_id_collection = False, query = None):

    from cocktail.persistence import PersistentObject

    if isinstance(subset, Query):
        return subset.execute()
    elif isinstance(subset, PersistentObject):
        return subset.id,
    elif is_id_collection:
        return subset
    else:
        warn(
            "Matching a subset with a collection of PersistentObject "
            "instances is discouraged, as the full state for those objects "
            "will have to be fetched, just to obtain their IDs. If possible, "
            "try to use ID collections or subqueries instead.\n"
            "Offending query: %s" % ("?" if query is None else repr(query)),
            stacklevel = 2
        )
        return (item.id for item in subset)

def _inclusion_resolution(self, query):

    subject = self.operands[0]
    subset = self.operands[1].eval()

    if subject is expressions.Self:

        ids = ids_from_subset(subset, self.by_key, query = query)

        def impl(dataset):
            dataset.intersection_update(ids)
            return dataset

        return ((-3, 0), impl)

    elif isinstance(subject, RelationMember) and subject.schema is query.type:

        ids = ids_from_subset(subset, self.by_key, query = query)
        index, index_kw = query._get_expression_index(self, subject)

        if index is not None:

            def impl(dataset):
                matches = set()
                for id in ids:
                    matches.update(index.values(key = id, **index_kw))
                dataset.intersection_update(matches)
                return dataset

            return ((-1, 0), impl)

    return ((0, 0), None)

expressions.InclusionExpression.resolve_filter = _inclusion_resolution

def _exclusion_resolution(self, query):

    subject = self.operands[0]
    subset = self.operands[1].eval()
    ids = ids_from_subset(subset, self.by_key, query = query)

    if subject is expressions.Self:

        def impl(dataset):
            dataset.difference_update(ids)
            return dataset

        return ((-3, 0), impl)

    elif isinstance(subject, RelationMember) and subject.schema is query.type:

        index, index_kw = query._get_expression_index(self, subject)

        if index is not None:

            def impl(dataset):
                matches = set()
                for id in ids:
                    matches.update(index.values(key = id, **index_kw))
                dataset.difference_update(matches)
                return dataset

            return ((-1, 0), impl)

    return ((0, 0), None)

expressions.ExclusionExpression.resolve_filter = _exclusion_resolution

# TODO: Provide an index aware custom implementation for StartsWithExpression
expressions.StartsWithExpression.resolve_filter = \
    lambda self, query: ((0, -1), None)

expressions.EndsWithExpression.resolve_filter = \
    lambda self, query: ((0, -1), None)

def _contains_resolution(self, query):

    subject = self.operands[0]

    if isinstance(subject, Collection):
        index, index_kw = query._get_expression_index(self, subject)
        if index is not None:
            def impl(dataset):
                item = self.operands[1].eval()
                k = subject.get_index_value(item)
                dataset.intersection_update(
                    index.values(key = k, **index_kw)
                )
                return dataset

            return ((-1, 0), impl)

    return ((0, -2), None)

expressions.ContainsExpression.resolve_filter = _contains_resolution

def _contains_any_resolution(self, query):

    subject = self.operands[0]

    if isinstance(subject, Collection):
        index, index_kw = query._get_expression_index(self, subject)
        if index is not None:
            def impl(dataset):
                subset = set()

                for item in self.operands[1].eval():
                    k = subject.get_index_value(item)
                    subset.update(index.values(key = k, **index_kw))

                dataset.intersection_update(subset)
                return dataset

            return ((-1, 1), impl)

    return ((0, -3), None)

expressions.ContainsAnyExpression.resolve_filter = _contains_any_resolution

def _contains_all_resolution(self, query):

    subject = self.operands[0]

    if isinstance(subject, Collection):
        index, index_kw = query._get_expression_index(self, subject)
        if index is not None:
            def impl(dataset):
                subset = None

                for item in self.operands[1].eval():
                    k = subject.get_index_value(item)
                    k_items = index.values(key = k, **index_kw)
                    if subset is None:
                        subset = set(k_items)
                    else:
                        subset.intersection_update(k_items)

                dataset.intersection_update(subset)
                return dataset

            return ((-1, 1), impl)

    return ((0, -3), None)

expressions.ContainsAllExpression.resolve_filter = _contains_all_resolution

def _lacks_resolution(self, query):

    subject = self.operands[0]

    if isinstance(subject, Collection):
        index, index_kw = query._get_expression_index(self, subject)
        if index is not None:
            def impl(dataset):
                item = self.operands[1].eval()
                k = subject.get_index_value(item)
                dataset.difference_update(
                    index.values(key = k, **index_kw)
                )
                return dataset

            return ((-1, 0), impl)

    return ((0, -2), None)

expressions.LacksExpression.resolve_filter = _lacks_resolution

expressions.MatchExpression.resolve_filter = \
    lambda self, query: ((0, -3), None)

def _has_resolution(self, query):

    index = self.relation.index

    if index is None:
        return ((1, 0), None)
    else:
        def impl(dataset):

            related_subset = \
                self.relation.related_type.select(self.filters).execute()

            if related_subset:

                subset = set()

                if not index.accepts_multiple_values:
                    for related_id in related_subset:
                        referer_id = index.get(related_id)
                        if referer_id is not None:
                            subset.add(referer_id)
                else:
                    for related_id in related_subset:
                        subset.update(index.values(key = related_id))

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

            subset = set(max_method(max = None, exclude_max = False))
            subset.update(
                max_method(min = min_value, exclude_min = self.exclude_min)
            )

            if max_value is not None:
                subset.intersection_update(
                    min_method(max = max_value, exclude_max = self.exclude_max)
                )

            dataset.intersection_update(subset)
            return dataset

        # One or both fields have non-unique indexes
        if min_index.accepts_multiple_values \
        or max_index.accepts_multiple_values:
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

        relation = self.relation

        if relation.related_end is not None:
            index, index_kw = \
                query._get_expression_index(self, relation.related_end)

            if index is not None:
                def impl(dataset):
                    descendants = set()
                    root_ids = ids_from_subset(
                        self.operands[1].eval(None),
                        query = query
                    )

                    if self.include_self:
                        descendants.update(root_ids)

                    def descend(parent_id):
                        for child_id in index.values(
                            key = parent_id,
                            **index_kw
                        ):
                            descendants.add(child_id)
                            descend(child_id)

                    for root_id in root_ids:
                        descend(root_id)

                    dataset.intersection_update(descendants)
                    return dataset

                return ((-1, 0), impl)

    return ((0, 0), None)

expressions.DescendsFromExpression.resolve_filter = _descends_from_resolution

def _search_resolution(self, query):

    indexed_member = None
    languages = None if self.languages is None else list(self.languages)

    # Searching over the whole text mass of the queried type
    if isinstance(self.subject, expressions.SelfExpression) \
    and query.type.full_text_indexed:
        indexed_member = query.type
        if languages is None:
            languages = [None, get_language()]
        elif None not in languages:
            languages.append(None)

    # Searching a specific text field
    elif isinstance(self.subject, Member) and self.subject.full_text_indexed:
        indexed_member = self.subject
        if languages is None:
            languages = [get_language() if self.subject.translated else None]

    # Should apply stemming?
    stemming = self.stemming
    if stemming is None and indexed_member is not None:
        stemming = indexed_member.stemming

    # No optimization available
    if indexed_member is None or stemming != indexed_member.stemming:
        return ((0, 0), None)

    # Full text index available
    else:
        def impl(dataset):

            subset = set()

            for language in languages:
                index = indexed_member.get_full_text_index(language)

                if self.match_mode == "whole_word":
                    search = index.search
                    terms = words.split(self.query, locale = language)

                elif self.match_mode == "prefix":
                    search = index.search_glob

                    if stemming:
                        terms = words.iter_stems(self.query, locale = language)
                    else:
                        query = words.normalize(self.query, locale = language)
                        terms = words.split(query, locale = language)

                    terms = [term + "*" for term in terms]

                elif self.match_mode == "pattern":
                    search = index.search_glob

                    if stemming:
                        terms = words.get_stems(
                            self.query,
                            locale = language,
                            preserve_patterns = True
                        )
                    else:
                        query = words.normalize(
                            self.query,
                            locale = language,
                            preserve_patterns = True
                        )
                        terms = words.split(
                            query,
                            locale = language,
                            preserve_patterns = True
                        )
                else:
                    raise ValueError(
                        "Invalid value for SearchExpression.match_mode: "
                        "expected one of 'whole_word', 'prefix' or 'pattern', "
                        "got %r instead" % self.match_mode
                    )

                if self.logic == "and":
                    language_subset = None

                    for term in terms:
                        results = search(term)
                        if not results:
                            language_subset = None
                            break

                        if language_subset is None:
                            language_subset = set(results.keys())
                        else:
                            language_subset.intersection_update(
                                iter(results.keys())
                            )

                    if language_subset is not None:
                        subset.update(language_subset)

                elif self.logic == "or":
                    for term in terms:
                        results = search(term)
                        if results:
                            subset.update(iter(results.keys()))

            dataset.intersection_update(subset)
            return dataset

        return ((-1, 1), impl)

expressions.SearchExpression.resolve_filter = _search_resolution

# Translation
#------------------------------------------------------------------------------
def _query_translation_factory(filtered_format):

    def translate_query(instance, **kwargs):

        subject = translations(instance.type, suffix = ".plural", **kwargs)

        if instance.filters:
            return filtered_format % {
                "subject": subject,
                "filters": ", ".join(
                    translations(filter)
                    for filter in instance.filters
                )
            }
        else:
            return subject

    return translate_query

translations.define(
    "cocktail.persistence.query.Query.instance",
    ca = _query_translation_factory(
        "%(subject)s que compleixen: %(filters)s"
    ),
    es = _query_translation_factory(
        "%(subject)s que cumplan: %(filters)s"
    ),
    en = _query_translation_factory(
        "%(subject)s filtered by: %(filters)s"
    )
)

ordered_collection_types = (list, tuple, ListWrapper, Query)

fast_membership_test_sequence_types = (
    set,
    IOTreeSet, IOSet,
    OOTreeSet, OOSet,
    Query
)

