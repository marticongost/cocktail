#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.modeling import getter
from cocktail.html import Element
from cocktail.html.selectors import DropdownSelector
from cocktail.controllers.viewstate import view_state


class Pager(Element):

    name = None
    item_count = 0
    page = 0
    page_size = 15
    hide_when_empty = True
    visible_pages = 10
    visible_pages_options = (10, 15, 20, 30, 50, 100)
    
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
            self.first_page_button["href"] = "?" + self._view_state(page = 0)
            self.previous_page_button["href"] = \
                "?" + self._view_state(page = self.page - 1)
        
        # Last page
        if self.page + 1 == page_count:
            self.next_page_button.visible = False
            self.last_page_button.visible = False
        else:
            self.next_page_button["href"] = \
                "?" + self._view_state(page = self.page + 1)
            self.last_page_button["href"] = \
                "?" + self._view_state(page = page_count - 1)

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
            self.page_links.append(page_link)

    def create_button(self, name):
        button = Element("a")
        button.add_class(name)
        button.append(Element("img", src = "/resources/images/%s.png" % name))
        return button

    def create_page_links(self):
        page_links = Element()
        page_links.add_class("page_links")
        return page_links

    def create_page_link(self, page):

        page_link = Element("a")
        page_link["href"] = "?" + self._view_state(page = page)
        page_link.append(str(page + 1))

        if page == self.page:
            page_link.add_class("selected")

        return page_link

    def _view_state(self, **params):
        return view_state(
            **dict(
                (self._get_qualified_name(param), value)
                for param, value in params.iteritems()
            )
        )

    def _get_qualified_name(self, param):
        return self.name + "_" + param if self.name else param

    @getter
    def page_count(self):
        div, mod = divmod(self.item_count, self.page_size)
        return div + 1 if mod else div

