#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.translations import translations
from cocktail.html import Element, templates


class PagingControls(Element):

    subset = None
    page = None
    page_size = None
    page_size_editable = True
    
    user_collection = None

    def _build(self):
        
        self.pager = self.create_pager()
        self.append(self.pager)

        self.item_count = self.create_item_count()
        self.append(self.item_count)       

    def _ready(self):

        Element._ready(self)

        if self.user_collection:
            self.subset = self.user_collection.subset
            self.page = self.user_collection.page
            self.page_size = self.user_collection.page_size
       
        if (not self.user_collection or self.user_collection.allow_paging) \
        and self.subset:

            subset_count = len(self.subset)

            # Pager
            self.pager.page = self.page
            self.pager.page_size = self.page_size
            self.pager.item_count = subset_count

            # Page size
            if self.page_size_editable:
                self.page_size_control = self.create_page_size_control()
                self.page_size_control.place_after(self.pager)

                self.page_size_control.input["value"] = \
                    str(self.page_size)

            # Item count
            self.item_count.append(translations("Item count",
                page_range = (                    
                    1 + self.page * self.page_size,
                    min(subset_count, (self.page + 1) * self.page_size)
                ),
                item_count = subset_count
            ))
        else:
            self.visible = False

    def create_pager(self):
        pager = templates.new("cocktail.html.Pager")
        return pager

    def create_page_size_control(self):
        
        control = Element()
        control.add_class("page_size")
        control.append(translations("Results per page"))
        
        control.input = Element("input", type = "text")
        control.input["name"] = "page_size"
        control.append(control.input)

        return control

    def create_item_count(self):
        item_count = Element()
        item_count.add_class("item_count")
        return item_count

