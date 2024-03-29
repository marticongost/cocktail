#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.events import when
from cocktail.translations import translations
from cocktail.html import Element
from cocktail.controllers.request import get_request_query


class Pager(Element):

    item_count = 0
    page = 0
    page_size = 15
    page_param_name = "page"
    name_prefix = None
    name_suffix = None
    hide_when_empty = True
    visible_pages = 10

    button_style = "characters"
    button_characters = {
        "first": "«",
        "last": "»",
        "previous": "&lt;",
        "next": "&gt;"
    }

    pagination = None
    user_collection = None

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self.button_characters = self.button_characters.copy()

    def _build(self):

        # Aproximate layout:
        # |<  <  1 2 [3] 4 5 6 7 8 9 10  >  >|

        self.first_page_button = self.create_button("first")
        self.append(self.first_page_button)

        self.previous_page_button = self.create_button("previous")
        self.append(self.previous_page_button)

        self.page_links = self.create_page_links()
        self.append(self.page_links)

        self.next_page_button = self.create_button("next")
        self.append(self.next_page_button)

        self.last_page_button = self.create_button("last")
        self.append(self.last_page_button)

    def _ready(self):

        Element._ready(self)

        if self.user_collection:
            self.page = self.user_collection.page
            self.page_size = self.user_collection.page_size
            self.page_param_name = \
                self.user_collection.params.get_parameter_name(
                    self.page_param_name
                )
            if self.user_collection.subset:
                self.item_count = len(self.user_collection.subset)
        elif self.pagination:
            self.page = self.pagination.current_page
            self.page_size = self.pagination.page_size
            self.page_param_name = \
                self.pagination.__class__.page.get_parameter_name(
                    prefix = self.name_prefix,
                    suffix = self.name_suffix
                )
            self.item_count = self.pagination.item_count

        page_count = self.page_count

        # Hide the pager when only one page is visible
        if self.hide_when_empty and page_count < 2:
            self.visible = False
            return

        # First page
        if self.page == 0:
            self.first_page_button.visible = False
            self.previous_page_button.visible = False
        else:
            self.first_page_button["href"] = self._get_page_link(0)
            self.previous_page_button["href"] = self._get_page_link(
                self.page - 1
            )

        # Last page
        if self.page + 1 == page_count:
            self.next_page_button.visible = False
            self.last_page_button.visible = False
        else:
            self.next_page_button["href"] = self._get_page_link(self.page + 1)
            self.last_page_button["href"] = self._get_page_link(
                self.page_count - 1
            )

        # Direct page links
        radius = self.visible_pages / 2
        start_page = self.page - radius
        end_page = self.page + radius

        if start_page < 0:
            end_page += abs(start_page)
        elif end_page >= page_count:
            start_page -= (end_page - page_count)

        if end_page - start_page >= self.visible_pages:
            end_page -= 1

        start_page = max(start_page, 0)
        end_page = min(end_page, page_count - 1)

        for page in range(start_page, end_page + 1):
            page_link = self.create_page_link(page)
            if page == end_page:
                page_link.add_class("last")
            self.page_links.append(page_link)

    def create_button(self, name):
        button = Element("a")
        button.add_class("button")
        button.add_class(name)
        button.icon = Element("img",
            src = "/resources/images/%s.png" % name,
            alt = translations("cocktail.html.Pager.%s_button" % name)
        )
        button.icon["title"] = button.icon["alt"]

        @when(button.icon.ready_stage)
        def set_button_style(e):
            if self.button_style == "characters":
                button.icon.tag = "span"
                button.icon["src"] = None
                button.icon["alt"] = None
                button.icon.append(self.button_characters[name])

        button.append(button.icon)
        return button

    def create_page_links(self):
        page_links = Element()
        page_links.add_class("page_links")
        return page_links

    def create_page_link(self, page):

        page_link = Element("a")
        page_link["href"] = self._get_page_link(page)
        page_link.append(str(page + 1))

        if page == self.page:
            page_link.add_class("selected")

        return page_link

    def _view_state(self, **params):
        return get_request_query(
            **dict(
                (self._get_qualified_name(param), value)
                for param, value in params.items()
            )
        )

    def _get_qualified_name(self, param):
        return self.name + "_" + param if self.name else param

    def _get_page_link(self, page_number):
        return "?" + self._view_state(**{str(self.page_param_name): page_number})

    @property
    def page_count(self):
        if not self.page_size:
            return 1
        else:
            div, mod = divmod(self.item_count, self.page_size)
            return div + 1 if mod else div

