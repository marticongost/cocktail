#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.translations import translate
from cocktail.html import (
    Element,
    Content,
    Table,
    PagingControls,
    MULTIPLE_SELECTION,
    CheckList,
    LinkSelector
)

class CollectionView(Element):

    tag = "form"

    cms = None
    backoffice = None
    user_collection = None
    actions = ()
    available_languages = None
    visible_languages = None

    def _build(self):

        self["method"] = "get"

        self.paging_controls = self.create_paging_controls()
        self.append(self.paging_controls)

        self.toolbar = self.create_toolbar()
        self.append(self.toolbar)

        self.collection_display = self.create_collection_display()
        self.append(self.collection_display)

    def _ready(self):

        Element._ready(self)

        self.paging_controls.user_collection = self.user_collection
        self.collection_display.user_collection = self.user_collection

        self._fill_toolbar_actions()

        # Visible members
        self.visible_members_selector.items = \
            self.user_collection.schema.ordered_members()

        self.visible_members_selector.value = self.user_collection.members

        # Visible languages
        self.visible_languages_selector.items = self.available_languages
        self.visible_languages_selector.value = self.visible_languages

        # View content
        if not self.user_collection.page_subset():
            self.view.append(Element("div", "no_results", [
                translate("No results")
            ]))

    PagingControls = PagingControls

    def create_paging_controls(self):
        controls = self.PagingControls()
        controls.add_class("paging")
        return controls
    
    def create_toolbar(self):
        
        toolbar = Element()
        toolbar.add_class("toolbar")

        self.actions_box = Element()
        self.actions_box.add_class("actions_box")
        toolbar.append(self.actions_box)

        self.settings_box = Element()
        self.settings_box.add_class("settings_box")
        toolbar.append(self.settings_box)

        # Visible members
        self.visible_members_control = self.create_visible_members_control()
        self.settings_box.append(self.visible_members_control)

        # Visible languages
        self.visible_languages_control = \
            self.create_visible_languages_control()
        self.settings_box.append(self.visible_languages_control)

        return toolbar
    
    def _fill_toolbar_actions(self):

        for action in self.actions:
            action_button = self.create_toolbar_button(action)
            setattr(self, action + "_button", action_button)
            self.actions_box.append(action_button)

    def create_toolbar_button(self, action):        
        button = Element("button", name = "section", value = action)
        button.add_class("toolbar_button")
        button.add_class(action)
        button.append(
            Element("img",
                src = self.cms.uri("resources", "images", action + ".png"))
        )
        button.append(Element("label", children = [translate(action)]))
        return button


    def create_visible_members_control(self):

        self.visible_members_selector = self.create_visible_members_selector()

        return Element("div", "toolbar_button selector visible_members", [
            Element("span", "label", [translate("Visible members")]),
            Element("div", "selector_content", [
                self.visible_members_selector,
                    Element("button",
                    name = "section",
                    value = "content",
                    children = [translate("Submit")]
                )
            ])            
        ])

    class VisibleMembersSelector(CheckList):

        def get_item_value(self, item):
            if isinstance(item, basestring):
                return item
            else:
                return item.name
        
        def get_item_label(self, member):
            return translate(member)

    def create_visible_members_selector(self):
        selector = self.VisibleMembersSelector()
        selector.name = "members"
        return selector

    def create_visible_languages_control(self):
        
        self.visible_languages_selector = \
            self.create_visible_languages_selector()
        
        return Element("div", "toolbar_button selector visible_languages", [
            Element("span", "label", [translate("Content languages")]),
            Element("div", "selector_content", [
                self.visible_languages_selector,
                Element("button",
                    name = "section",
                    value = "content",
                    children = [translate("Submit")]
                )
            ])
        ])

    class VisibleLanguagesSelector(CheckList):
        pass

    def create_visible_languages_selector(self):
        selector = self.VisibleLanguagesSelector()
        selector.name = "language"
        return selector
 
    CollectionDisplay = Table

    def create_collection_display(self):
        display = self.CollectionDisplay()
        display.add_class("collection_display")        
        return display

