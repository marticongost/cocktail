#-*- coding: utf-8 -*-
u"""Defines the `Pagination` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import getter
from cocktail import schema


class Pagination(schema.SchemaObject):
    """A pagination over an ordered collection of items."""

    __item_count = None

    page = schema.Integer(
        required = True,
        default = 0,
        min = lambda ctx: -ctx.validable.page_count,
        max = lambda ctx: ctx.validable.page_count - 1
    )

    page_size = schema.Integer(
        required = True,
        min = 0,
        default = 10
    )

    items = None

    def _get_item_count(self):
        if self.__item_count is not None:
            return self.__item_count
            
        if self.items is not None:
            return len(self.items)

        return 0

    def _set_item_count(self, value):

        if value is not None:

            if not isinstance(value, int):
                raise TypeError(
                    "Pagination.item_count should be an integer, got %s "
                    "instead" % type(value)
                )

            if value < 0:
                raise ValueError(
                    "Can't set Pagination.item_count to a negative value"
                )

        self.__item_count = value

    item_count = property(_get_item_count, _set_item_count,
        doc = """The number of items to paginate."""
    )

    @getter
    def page_count(self):
        """The total number of pages needed to cover the full item count."""
        if not self.page_size:
            return 1
        else:
            return -(-self.item_count / self.page_size) # Fast ceiling division trick

    @getter
    def current_page(self):
        """Gives the ordinal position of the currently selected page, starting
        at 0.

        This property will usually be equivalent to `page`, but it normalizes
        negative indices to positive values.
        """
        page = self.page
        if page is not None and page < 0:
            page = self.page_count + page
        return page

    @getter
    def current_page_items(self):
        """The items in the selected page."""
        if self.items is None:
            raise ValueError(
                "Can't retrieve Pagination.page_items if the 'items' "
                "property has not been set"
            )

        return self.items[self.start:self.end]

    @getter
    def current_page_size(self):
        """The number of items in the selected page."""
        return self.end - self.start

    @getter
    def start(self):
        """The ordinal position in the item set where the selected page starts
        (inclusive).
        """
        if self.page is None or not self.page_size:
            return 0
        else:
            return min(
                self.current_page * self.page_size,
                max(0, self.item_count - 1)
            )

    @getter
    def end(self):
        """The ordinal position in the item set where the selected page ends
        (exclusive).
        """
        if not self.page_size:
            return self.item_count
        else:
            return min((self.current_page + 1) * self.page_size, self.item_count)
    @getter
    def at_first_page(self):
        """Indicates if the selected page is the first one."""
        return self.current_page == 0

    @getter
    def at_last_page(self):
        """Indicates if the selected page is the last one."""
        return self.current_page + 1 == self.page_count

    def page_for(self, item):
        """Indicates the page that contains the specified item."""
        if self.items is None:
            raise ValueError(
                "Can't call Pagination.page_for() if the 'items' property has "
                "not been set"
            )

        if not self.page_size:
            return 0

        for i, pagination_item in enumerate(self.items):
            if item == pagination_item:
                return i / self.page_size

        return None

