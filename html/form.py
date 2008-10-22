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
from cocktail.html import Element, templates
from cocktail.html.datadisplay import DataDisplay
from cocktail.html.hiddeninput import HiddenInput


class Form(Element, DataDisplay):

    tag = "form"
    translations = None
    hide_empty_fieldsets = True
    errors = None
    hidden = False
    embeded = False

    def __init__(self, *args, **kwargs):
        DataDisplay.__init__(self)

        self.set_member_type_display(Member,
            templates.get_class("cocktail.html.TextBox"))

        self.set_member_type_display(Boolean,
            templates.get_class("cocktail.html.CheckBox"))

        self.set_member_type_display(Reference,
            templates.get_class("cocktail.html.DropdownSelector"))

        self.__groups = []
        self.groups = ListWrapper(self.__groups)
        self.__hidden_members = {}
        Element.__init__(self, *args, **kwargs)

    def _build(self):

        self.fields = Element()
        self.fields.add_class("fields")
        self.append(self.fields)

        self.buttons = Element()
        self.buttons.add_class("buttons")
        self.append(self.buttons)

        self.submit_button = Element("button")
        self.submit_button["name"] = "submit"
        self.submit_button["value"] = "true"
        self.submit_button["type"] = "submit"
        self.submit_button.append(translate("Submit"))
        self.buttons.append(self.submit_button)

    def _ready(self):
        self._fill_fields()

        if self.embeded:
            self.tag = "fieldset"
            self.buttons.visible = False

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
                    setattr(self, member.name + "_field", field_entry)
    
    def create_fieldset(self, group):

        fieldset = Element("fieldset")
        fieldset.add_class(group.id)
        
        fieldset.legend = Element("legend")
        fieldset.legend.append(translate(self.schema.name + "." + group.id))
        fieldset.append(fieldset.legend)

        return fieldset

    def create_field(self, member):

        hidden = self.get_member_hidden(member)

        # Container
        field_entry = Element()
        
        if hidden:
            field_entry.tag = None
        else:
            field_entry.add_class("field")
            field_entry.add_class(member.name + "_field")
             
            if member.required:
                field_entry.add_class("required")

            # Label
            field_entry.label = self.create_field_label(member)
            field_entry.append(field_entry.label)

        # Control:

        # Translated member
        if member.translated and self.translations:
            
            if not hidden:
                field_entry.add_class("translated")

            current_language = get_content_language()

            for language in self.translations:
                
                set_content_language(language)

                if hidden:
                    control_container = field_entry
                    control = self.create_hidden_input(self.data, member)
                else:
                    control_container = Element()
                    control_container.add_class("language")
                    control_container.add_class(language)
                    field_entry.append(control_container)                    
                    control = self.create_control(self.data, member)

                control.language = language
                control_container.append(control)

            set_content_language(current_language)

        # Regular member
        else:
            if hidden:
                field_entry.control = self.create_hidden_input(
                    self.data,
                    member)
            else:
                field_entry.control = self.create_control(self.data, member)

            field_entry.append(field_entry.control)

        return field_entry

    def create_hidden_input(self, obj, member):
        input = HiddenInput()        
        input.data = obj
        input.member = member
        input.value = self.get_member_value(obj, member)
        return input

    def create_control(self, obj, member):
        control = DataDisplay.get_member_display(self, obj, member)
        control.add_class("control")

        if self.errors and self.errors.in_member(
            member,
            member.translated and get_content_language() or None
        ):
            control.add_class("error")

        return control
    
    def create_field_label(self, member):        
        label = Element("label")
        label["for"] = member.name
        label.append(self.get_member_label(member))       
        return label

    def add_group(self, group_id, members_filter):
        self.__groups.append(FormGroup(self, group_id, members_filter))

    def get_member_hidden(self, member):
        key = self._normalize_member(member)
        return self.__hidden_members.get(key, self.hidden)

    def set_member_hidden(self, member, hidden):
        key = self._normalize_member(member)
        self.__hidden_members[key] = hidden


class FormGroup(object):

    def __init__(self, form, id, members_filter):
        self.__form = form
        self.__id = id
        self.__members_filter = members_filter

        if callable(members_filter):
            self.__match_expr = members_filter
        else:
            members = set(self.__form._normalize_member(member)
                          for member in members_filter)

            self.__match_expr = \
                lambda member: self.__form._normalize_member(member) in members

    @getter
    def form(self):
        return self.__form

    @getter
    def id(self):
        return self.__id

    @getter
    def members_filter(self):
        return self.__members_filter

    def matches(self, member):
        return self.__match_expr(member)

