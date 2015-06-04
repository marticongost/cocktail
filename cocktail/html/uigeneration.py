#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.translations import get_language
from cocktail.html.element import Element
from cocktail.html import templates
import cocktail.controllers.parameters
from cocktail.controllers.fileupload import FileUpload

def display_factory(display_name, **kwargs):
    """A convenience function to customize displays for schema members.

    @param display_name: A fully qualified name of an
        L{Element<element.Element>} subclass or CML template.
    @type display_name: str

    @param kwargs: HTML or Python attributes to set on the display.

    @return: A function that produces displays of the indicated kind,
        initialized with the supplied parameters.
    @rtype: L{Element<element.Element>}
    """
    def func(ui_generation, obj, member, value, **context):
        display = templates.new(display_name)

        for k, v in kwargs.iteritems():
            if hasattr(display, k):
                setattr(display, k, v)
            else:
                display[k] = v

        return display

    return func


class UIGenerator(object):

    base_ui_generators = []
    read_only_ui_generator = None

    def __init__(self,
        display_property = None,
        member_type_displays = None,
        base_ui_generators = None
    ):
        if display_property and not hasattr(schema.Member, display_property):
            schema.Member.display_property = None

        self.__display_property = display_property
        self.base_ui_generators = list(
            base_ui_generators
            or self.base_ui_generators
        )
        self.__member_displays = {}

        if member_type_displays is None:
            self.__member_type_displays = {}
        else:
            self.__member_type_displays = dict(member_type_displays)

    def __repr__(self):
        desc = self.__class__.__name__
        if self.__display_property:
            desc += "<%s>" % self.__display_property
        if self.base_ui_generators:
            desc += "(%s)" % ", ".join(
                UIGenerator.__repr__(ui_generator)
                for ui_generator in self.base_ui_generators
            )
        return desc

    @property
    def display_property(self):
        return self.__display_property

    def ui_generator_chain(self):

        full_chain = list(self._iter_generator_chain())
        full_chain.reverse()
        normalized_chain = []

        for ui_generator in full_chain:
            if ui_generator not in normalized_chain:
                normalized_chain.append(ui_generator)

        normalized_chain.reverse()
        return normalized_chain

    def _iter_generator_chain(self):
        yield self
        for base in self.base_ui_generators:
            for ancestor in base._iter_generator_chain():
                yield ancestor

    def get_member_type_display(self, member_type):
        return self.__member_type_displays.get(member_type)

    def set_member_type_display(self, member_type, display):
        self.__member_type_displays[member_type] = display

    def create_object_display(self, obj, **context):
        return self.create_member_display(None, obj.__class__, obj, **context)

    def create_member_display(self, obj, member, value, **context):

        if member.editable == schema.READ_ONLY:
            for ui_generator in self._iter_generator_chain():
                if ui_generator.read_only_ui_generator:
                    display = (
                        ui_generator.read_only_ui_generator
                        .create_member_display(
                            obj,
                            member,
                            value,
                            **context
                        )
                    )
                    display["data-cocktail-editable"] = "read_only"
                    return display

        for display in self._iter_member_displays(
            obj,
            member,
            value,
            **context
        ):
            if display is not None:
                display = self._normalize_member_display(
                    obj,
                    member,
                    value,
                    display,
                    **context
                )
                if display is not None:
                    if self.read_only_ui_generator:
                        display["data-coktail-editable"] = "editable"
                    return display

        raise ValueError(
            "%r couldn't find a valid display for %r" % (self, member)
        )

    def _iter_member_displays(
        self,
        obj,
        member,
        value,
        **context
    ):
        chain = self.ui_generator_chain()

        for ui_generator in chain:
            for display in ui_generator._iter_per_member_displays(
                obj,
                member,
                value,
                **context
            ):
                yield display

        mro = [cls
               for cls in member.__class__.__mro__
               if issubclass(cls, schema.Member)]

        if isinstance(member, schema.SchemaClass):
            mro = [cls
                   for cls in member.__mro__
                   if isinstance(cls, schema.SchemaClass)] + mro

        for cls in mro:
            for ui_generator in chain:
                for display in ui_generator._iter_per_member_type_displays(
                    obj,
                    member,
                    value,
                    cls,
                    **context
                ):
                    yield display

    def _iter_per_member_displays(
        self,
        obj,
        member,
        value,
        **context
    ):
        if self.__display_property:
            yield getattr(member, self.__display_property, None)

    def _iter_per_member_type_displays(
        self,
        obj,
        member,
        value,
        member_type,
        **context
    ):
        yield self.__member_type_displays.get(member_type)

    def _normalize_member_display(
        self,
        obj,
        member,
        value,
        display,
        **context
    ):
        if isinstance(display, type) and issubclass(display, Element):
            display = display()
        elif callable(display):
            method_subject = getattr(display, "im_self", None)
            if method_subject is self:
                display = display(obj, member, value, **context)
            else:
                display = display(self, obj, member, value, **context)

        if isinstance(display, basestring):
            display = templates.new(display)

        if display is not None:

            if not display.is_valid_display(
                self,
                obj,
                member,
                value,
                **context
            ):
                return None

            display.ui_generator = self
            display.data = obj
            display.member = member
            display.language = get_language()
            display.value = value

            for key, value in context.iteritems():
                setattr(display, key, value)

        return display


# default UI generator (read only)
#------------------------------------------------------------------------------
def _reference_default_display(ui_generator, obj, member, value, **context):
    if value is not None and not member.class_family:
        return ui_generator.create_object_display(value, **context)

default_display = UIGenerator("display", {
    schema.Member: "cocktail.html.ValueDisplay",
    schema.Collection: "cocktail.html.List",
    schema.Mapping: "cocktail.html.MappingTable",
    schema.Reference: _reference_default_display,
    schema.Color: "cocktail.html.ColorDisplay"
})

# default UI generator (editable)
#------------------------------------------------------------------------------
class EditControlGenerator(UIGenerator):

    enumeration_display = "cocktail.html.DropdownSelector"
    read_only_ui_generator = default_display

    def _iter_per_member_type_displays(
        self,
        obj,
        member,
        value,
        member_type,
        **context
    ):
        # If the member defines an enumeration, disregard its regular display,
        # and use a control that can display a set of values (typically, a
        # <select> element).
        if member.enumeration is not None:
            yield self.get_display_for_member_with_enumeration(
                obj,
                member,
                value,
                **context
            )

        for display in UIGenerator._iter_per_member_type_displays(
            self,
            obj,
            member,
            value,
            member_type,
            **context
        ):
            yield display

    def get_display_for_member_with_enumeration(
        self,
        obj,
        member,
        value,
        **context
    ):
        return self.enumeration_display


def embeded_form(ui_generator, obj, member, value, **context):
    form = templates.new("cocktail.html.Form")
    form.tag = "div"
    form.embeded = True
    form.schema = member
    form.name_prefix = getattr(ui_generator, "name_prefix", None)
    form.name_suffix = getattr(ui_generator, "name_suffix", None)
    return form

def _default_collection_edit_control(
    ui_generator,
    obj,
    member,
    value,
    **context
):
    if isinstance(member.items, FileUpload) and member.items.async:
        return "cocktail.html.AsyncFileUploader"
    elif member.items.enumeration is not None or member.is_persistent_relation:
        return "cocktail.html.CheckList"
    else:
        return "cocktail.html.CollectionEditor"

def _default_code_block_edit_control(
    ui_generator,
    obj,
    member,
    value,
    **context
):
    display = templates.new("cocktail.html.CodeEditor")
    display.syntax = member.language
    if member.language == "python":
        display.cols = 80
    return display

def _default_file_upload_edit_control(
    ui_generator,
    obj,
    member,
    value,
    **context
):
    if member.async:
        return "cocktail.html.AsyncFileUploader"
    else:
        return "cocktail.html.FileUploadBox"

default_edit_control = EditControlGenerator("edit_control", {
    schema.String: "cocktail.html.TextBox",
    schema.Boolean: "cocktail.html.CheckBox",
    schema.Reference: "cocktail.html.DropdownSelector",
    schema.BaseDateTime: "cocktail.html.DatePicker",
    schema.Number: "cocktail.html.NumberBox",
    schema.Decimal: "cocktail.html.TextBox",
    schema.Money: "cocktail.html.MoneyBox",
    schema.PhoneNumber: "cocktail.html.PhoneNumberBox",
    schema.URL: "cocktail.html.URLBox",
    schema.EmailAddress: "cocktail.html.EmailAddressBox",
    schema.Color: "cocktail.html.ColorPicker",
    schema.Month: "cocktail.html.DropdownSelector",
    schema.HTML: "cocktail.html.TinyMCE",
    schema.IBAN: "cocktail.html.IBANEntry",
    schema.SWIFTBIC: "cocktail.html.SWIFTBICEntry",
    schema.BankAccountNumber: "cocktail.html.MaskedInputBox",
    schema.Schema: embeded_form,
    schema.Collection: _default_collection_edit_control,
    schema.Mapping: "cocktail.html.MappingEditor",
    schema.CodeBlock: _default_code_block_edit_control,
    schema.GeoCoordinates: "cocktail.html.TextBox",
    FileUpload: _default_file_upload_edit_control
})

# default control in search forms
#------------------------------------------------------------------------------
default_search_control = UIGenerator(
    "search_control",
    base_ui_generators = [default_edit_control]
)

