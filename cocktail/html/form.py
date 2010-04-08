#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from __future__ import with_statement
from cocktail.translations import get_language, language_context
from cocktail.modeling import getter, ListWrapper
from cocktail.translations import translations
from cocktail.schema import (
    Member, Boolean, Reference, BaseDateTime, Decimal, Collection
)
from cocktail.controllers.fileupload import FileUpload
from cocktail.html import Element
from cocktail.html.datadisplay import DataDisplay
from cocktail.html.hiddeninput import HiddenInput

# Extension property that allows members to define their appearence in HTML
# forms
Member.edit_control = None


class Form(Element, DataDisplay):
    """A class that generates HTML forms from a schema description.

    @var errors: A list of validation errors, used to highlight fields with
        incorrect values.
    @type errors: L{ErrorList<cocktail.schema.errorlist.ErrorList>}

    @var embeded: When set to True, the form turns into a fieldset, to be
        nested inside other forms.
    @type embeded: bool

    @var required_marks: Sets wether a small visual clue should be added next
        to required fields.
    @type required_marks: bool

    @var table_layout: Determines if the form should use a table to align its
        fields.
    @type table_layout: bool

    @var default_button: A reference to one of the form's buttons. When set,
        the referenced button is duplicated, hidden and inserted at the start
        of the form, which makes that button act as the default for the whole
        form. This can be very useful when dealing with multiple buttons on a
        single form. Doesn't apply to L{embeded} forms.
    @type default_button: L{Element<cocktail.html.element.Element>}
    
    @var generate_fields: Indicates if the form should automatically create
        entries for all fields defined by its assigned schema. This is the
        default behavior; When set to False, filling the form will be left to
        the client code.
    @type generate_fields: bool

    @var generate_groups: Indicates if the form should automatically create the
        same field groups defined by its assigned schema. This is the default
        behavior; When set to False, only groups explicitly defined by the
        client code will be taken into account.
    @type generate_groups: bool
    """

    tag = "form"
    translations = None
    hide_empty_fieldsets = True
    errors = None
    hidden = False
    embeded = False
    required_marks = True
    table_layout = False
    default_button = None
    generate_fields = True
    generate_groups = True

    def __init__(self, *args, **kwargs):
        DataDisplay.__init__(self)

        self.set_member_type_display(
            Boolean, "cocktail.html.CheckBox")

        self.set_member_type_display(
            Reference, "cocktail.html.DropdownSelector")
            
        self.set_member_type_display(
            BaseDateTime, "cocktail.html.DatePicker")

        self.set_member_type_display(
            Decimal, "cocktail.html.DecimalBox")

        self.set_member_type_display(
            FileUpload, "cocktail.html.FileUploadBox")

        self.set_member_type_display(
            Collection, "cocktail.html.CheckList")

        self.__groups = []
        self.groups = ListWrapper(self.__groups)
        self.__hidden_members = {}
        Element.__init__(self, *args, **kwargs)

    def _build(self):
        
        self.add_resource("/cocktail/scripts/form.js")

        self.fields = Element()
        self.fields.add_class("fields")
        self.append(self.fields)

        self.buttons = Element()
        self.buttons.add_class("buttons")
        self.append(self.buttons)

        self.submit_button = Element("button")
        self.submit_button["value"] = "true"
        self.submit_button["type"] = "submit"
        self.submit_button.append(translations("Submit"))
        self.buttons.append(self.submit_button)
        self.default_button = self.submit_button

    def _ready(self):
        self._fill_fields()

        if self.embeded:
            if self.tag == "form":
                self.tag = "fieldset"
            self.buttons.visible = False

        elif self.default_button:
            hidden_button = Element(self.default_button.tag)
            for key, value in hidden_button.attributes.itervalues():
                hidden_button[key] = value
            hidden_button.set_style("display", "none")
            self.insert(0, hidden_button)

    def _fill_fields(self):
        if self.schema and self.generate_fields:

            if not self.__groups and self.generate_groups:
                schema_groups = self.displayed_members_by_group
                if len(schema_groups) > 1:
                    for group_name, members in schema_groups:
                        self.add_group(
                            group_name or "default",
                            set(member.name for member in members)
                        )

            if self.__groups:                
                members = self.displayed_members

                for group in self.__groups:

                    fieldset = self.create_fieldset(group)
                    self.fields.append(fieldset)
                    setattr(self, group.id + "_fieldset", fieldset)

                    if self.table_layout:
                        container = Element("table")
                        fieldset.append(container)
                    else:
                        container = fieldset

                    has_match = False
                    remaining_members = []

                    for member in members:
                        if group.matches(member):
                            field_entry = self.create_field(member)
                            container.append(field_entry)
                            self.build_member_explanation(member, field_entry)
                            setattr(self, member.name + "_field", field_entry)
                            has_match = True
                        else:
                            remaining_members.append(member)

                    members = remaining_members

                    if self.hide_empty_fieldsets and not has_match:
                        fieldset.visible = False
            else:
                if self.table_layout:
                    self.fields.tag = "table"

                for member in self.displayed_members:
                    field_entry = self.create_field(member)
                    self.fields.append(field_entry)
                    self.build_member_explanation(member, field_entry)
                    setattr(self, member.name + "_field", field_entry)
    
    def create_fieldset(self, group):

        group_id = group.id

        fieldset = Element("fieldset") 
        fieldset.add_class(group_id)

        label = self.get_group_label(group_id)
        if label:            
            fieldset.legend = Element("legend")
            fieldset.legend.append(label)
            fieldset.append(fieldset.legend)
        else:
            fieldset.legend = None
            fieldset.add_class("anonymous")

        return fieldset

    def create_field(self, member):

        hidden = self.get_member_hidden(member)
        
        entry = Element("tr" if self.table_layout else "div")

        if hidden:
            entry.tag = None
        else:
            entry.add_class("field")
            entry.add_class(member.name + "_field")
             
            if member.required:
                entry.add_class("required")

        def create_instance(language = None):
            if hidden:
                with language_context(language):
                    return self.create_hidden_input(self.data, member)
            else:
                return self.create_field_instance(member, language)

        if member.translated:
            entry.add_class("translated")
            for language in (self.translations or (get_language(),)):
                field_instance = create_instance(language)
                field_instance.add_class(language)
                entry.append(field_instance)
        else:
            entry.append(create_instance())
        
        return entry

    def build_member_explanation(self, member, entry):
        explanation = member.get_member_explanation()
        if explanation:
            entry.explanation = \
                self.create_member_explanation(member, explanation)

            if self.table_layout:
                entry.explanation.tag = "td"
                row = Element("tr")
                row.add_class("explanation_row")
                row.append(entry.explanation)
                entry.parent.append(row)
            else:
                entry.append(entry.explanation)

    def create_member_explanation(self, member, explanation):
        label = Element()
        label.add_class("explanation")
        label.append(explanation)
        return label

    def create_field_instance(self, member, language = None):

        field_instance = Element("td" if self.table_layout else "div")
        field_instance.add_class("field_instance")
    
        # Label
        field_instance.label = self.create_label(member, language)
        field_instance.append(field_instance.label)
        
        # Control
        with language_context(language):
            field_instance.control = self.create_control(self.data, member)

        if field_instance.control.class_css:
            for class_name in field_instance.control.class_css.split(" "):
                field_instance.add_class("field_instance-" + class_name)

        insert = getattr(field_instance.control, "insert_into_form", None)

        if insert:
            insert(self, field_instance)
        else:
            field_instance.append(field_instance.control)

        field_instance.label["for"] = field_instance.control.require_id()

        return field_instance

    def create_hidden_input(self, obj, member):

        input = HiddenInput()
        input.data = obj
        input.member = member
        input.value = self.get_member_value(obj, member)

        if member.translated:
            input.language = get_language()

        return input

    def create_label(self, member, language = None):
        
        label = Element("label")
        text = self.get_member_label(member)
        
        if text:
            label.label_title = self.create_label_title(member, text)
            label.append(label.label_title)
            
            if language:
                
                label.label_language = self.create_language_label(
                    member,
                    language)

                label.append(label.label_language)

            if self.required_marks \
            and member.required \
            and not isinstance(member, Collection):
                label.required_mark = self.create_required_mark(member)
                label.append(label.required_mark)
        else:
            label.visible = False

        return label

    def create_label_title(self, member, text):
        label_title = Element("span")
        label_title.add_class("label_title")
        label_title.append(text)
        return label_title

    def create_language_label(self, member, language):
        label = Element("span")
        label.add_class("language")
        label.append("(" + translations(language) + ")")
        return label

    def create_required_mark(self, member):
        mark = Element("span")
        mark.add_class("required_mark")
        mark.append("*")
        return mark

    def get_member_supplied_display(self, obj, member):
        return member.edit_control

    def default_display(self, obj, member):
        if member.enumeration is not None:
            return "cocktail.html.DropdownSelector"
        else:
            return "cocktail.html.TextBox"

    def create_control(self, obj, member):
        control = self.get_member_display(obj, member)
        control.add_class("control")

        if self.errors and self.errors.in_member(
            member,
            member.translated and get_language() or None
        ):
            control.add_class("error")

        return control   

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

