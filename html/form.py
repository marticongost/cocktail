#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.language import get_content_language, set_content_language
from cocktail.modeling import getter, ListWrapper
from cocktail.translations import translate
from cocktail.schema import Member, Boolean, Reference
from cocktail.html.element import Element
from cocktail.html.datadisplay import DataDisplay
from cocktail.html.textbox import TextBox
from cocktail.html.checkbox import CheckBox
from cocktail.html.selectors import DropdownSelector


class Form(Element, DataDisplay):

    tag = "form"
    translations = None
    hide_empty_fieldsets = True

    def __init__(self, *args, **kwargs):
        DataDisplay.__init__(self)
        self.set_member_type_display(Member, TextBox)
        self.set_member_type_display(Boolean, CheckBox)
        self.set_member_type_display(Reference, DropdownSelector)
        self.__groups = []
        self.groups = ListWrapper(self.__groups)
        Element.__init__(self, *args, **kwargs)

    def _build(self):

        self.fields = Element()
        self.fields.add_class("fields")
        self.append(self.fields)

        self.buttons = Element()
        self.buttons.add_class("buttons")
        self.append(self.buttons)

        self.submit_button = Element("button")
        self.submit_button["type"] = "submit"
        self.submit_button.append(translate("Submit"))
        self.buttons.append(self.submit_button)

    def _ready(self):
        self._fill_fields()

    def _fill_fields(self):
        if self.schema:
            if self.__groups:
                members = self.displayed_members

                for group in self.__groups:

                    fieldset = self.create_fieldset(group)
                    self.fields.append(fieldset)
                    setattr(self, group.id + "_fieldset", fieldset)

                    has_match = False
                    remaining_members = []

                    for member in members:
                        if group.matches(member):
                            field_entry = self.create_field(member)
                            fieldset.append(field_entry)
                            has_match = True
                        else:
                            remaining_members.append(member)

                    members = remaining_members

                    if self.hide_empty_fieldsets and not has_match:
                        fieldset.visible = False
            else:
                for member in self.displayed_members:
                    field_entry = self.create_field(member)
                    self.fields.append(field_entry)
    
    def create_fieldset(self, group):

        fieldset = Element("fieldset")
        fieldset.add_class(group.id)
        
        fieldset.legend = Element("legend")
        fieldset.legend.append(translate(self.schema.name + "." + group.id))
        fieldset.append(fieldset.legend)

        return fieldset

    def create_field(self, member):
        
        # Container
        field_entry = Element()
        field_entry.add_class("field")
        field_entry.add_class(member.name + "_field")
             
        if member.required:
            field_entry.add_class("required")

        # Label
        field_entry.label = self.create_field_label(member)
        field_entry.append(field_entry.label)

        # Control
        if member.translated and self.translations:
            
            field_entry.add_class("translated")

            current_language = get_content_language()

            for language in self.translations:
                set_content_language(language)
                
                control_container = Element()
                control_container.add_class("language")
                control_container.add_class(language)
                field_entry.append(control_container)

                control = self.get_member_display(self.data, member)
                control.language = language
                control_container.append(control)

            set_content_language(current_language)
        else:
            field_entry.control = self.get_member_display(self.data, member)
            field_entry.append(field_entry.control)

        return field_entry

    def get_member_display(self, obj, member):
        display = DataDisplay.get_member_display(self, obj, member)
        display.add_class("control")
        return display

    def create_field_label(self, member):        
        label = Element("label")
        label["for"] = member.name
        label.append(self.get_member_label(member))       
        return label

    def add_group(self, group):
        self.__groups.append(group)


class FormGroup(object):

    def __init__(self, id, members_filter):        
        self.__id = id
        self.__members_filter = members_filter

        if callable(members_filter):
            self.__match_expr = members_filter
        else:
            members = set(self._normalize_member(member)
                          for member in members_filter)

            self.__match_expr = \
                lambda member: self._normalize_member(member) in members

    @getter
    def id(self):
        return self.__id

    @getter
    def members_filter(self):
        return self.__members_filter

    def matches(self, member):
        return self.__match_expr(member)

