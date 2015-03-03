#-*- coding: utf-8 -*-
u"""
Visual elements for data binding.

@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         July 2008
"""
from cocktail import schema
from cocktail.modeling import getter, ListWrapper, empty_list
from cocktail.translations import translations, require_language

# IMPORTANT: importing 'display_factory' is required for backwards
# compatibility
from cocktail.html.uigeneration import (
    UIGenerator,
    default_display,
    display_factory
)


class DataDisplay(UIGenerator):
    "Base class for all visual components that can display schema-based data."

    base_ui_generators = [default_display]
    persistent_object = None
    schema = None
    editable = True
    translations = None
    accessor = None
    name_prefix = None
    name_suffix = None

    def __init__(self):
        UIGenerator.__init__(self)
        self.__member_displayed = {}
        self.__member_labels = {}
        self.__member_editable = {}
        self.__member_expressions = {}
        self.__member_displays = {}

    def _resolve_member(self, member):

        if isinstance(member, basestring):
            if self.schema is None:
                raise ValueError(
                    "Can't resolve a member by name on an unbound data display"
                )
            return self.schema[member]
        else:
            return member

    def _normalize_member(self, member):
        if isinstance(member, basestring):
            return member

        if self.schema is None:
            return member.name

        name = member.name

        if self.schema is not None:
            while member.schema is not None \
            and member.schema is not self.schema:
                member = member.schema
                name = member.name + "." + name

        return name

    @getter
    def displayed_members(self):
        if not self.schema:
            return empty_list
        else:
            return (member
                for member in self.schema.ordered_members(True)
                if self.get_member_displayed(member))

    @getter
    def displayed_members_by_group(self):
        if not self.schema:
            return empty_list
        else:
            members_by_group = []

            for group, group_members in self.schema.grouped_members():
                displayed_members = [
                    member
                    for member in group_members
                    if self.get_member_displayed(member)
                ]
                if displayed_members:
                    members_by_group.append((group, displayed_members))

            return members_by_group

    def get_member_name(self, member, language = None):
        return member.get_parameter_name(
            language = member.translated and self.translations and language,
            prefix = self.name_prefix,
            suffix = self.name_suffix
        )

    def get_member_displayed(self, member):
        """Indicates if the specified member should be displayed. By default,
        all members in the schema are displayed. The precise meaning of hiding
        a member will change between different implementors of the
        L{DataDisplay} interface. For example, a data table may still generate
        the HTML for a hidden column, but hide it using a CSS declaration, so
        that its visibility can be toggled later on using client side
        scripting. Members that shouldn't be shown at all shouldn't appear on
        the schema provided to the data display (possibly by excluding them
        using an `~cocktail.schema.adapter.Adapter`).

        @param member: The member to get the display state for. Can be
            specified using a direct reference to the member object, or by
            name.
        @type member: str or L{Member<cocktail.schema.member.Member>}

        @return: True if the member should be displayed, False otherwise.
        @rtype: bool
        """
        return self.__member_displayed.get(
                    self._normalize_member(member),
                    True)

    def set_member_displayed(self, member, displayed):
        """Establishes if the indicated member should be displayed. See
        L{get_member_displayed} for more details.

        @param member: The member to get the display state for. Can be
            specified using a direct reference to the member object, or by
            name.
        @type member: str or L{Member<cocktail.schema.member.Member>}

        @param displayed: True if the member should be displayed, False
            otherwise.
        @type displayed: bool
        """
        self.__member_displayed[self._normalize_member(member)] = displayed

    def get_member_label(self, member):
        """Gets the descriptive, human readable title for the member, as shown
        by the data display.

        @param member: The member to get the label for. Can be specified using
            a direct reference to the member object, or by name.
        @type member: str or L{Member<cocktail.schema.member.Member>}

        @return: The descriptive title for the member.
        @rtype: unicode
        """
        label = self.__member_labels.get(self._normalize_member(member), None)

        if label is None:
            label = translations(self._resolve_member(member))

        return label

    def set_member_label(self, member, label):
        """Sets the descriptive, human readable title for the member.

        @param member: The member to set the label for. Can be specified using
            a direct reference to the member object, or by name.
        @type member: str or L{Member<cocktail.schema.member.Member>}

        @param label: The descriptive title that will be assigned to the
            member.
        @type label: unicode
        """
        self.__member_labels[self._normalize_member(member)] = label

    def get_group_label(self, group):

        if self.schema:
            label = self.schema.translate_group(group)
            if label:
                return label

        if self.persistent_object:
            return self.persistent_object.__class__.translate_group(group)

    def get_member_editable(self, member):
        """Indicates if the given member should be editable by users. This
        affects the kind of display used by the member (for example, a text
        entry widget for an editable member, a static text label for a non
        editable one).

        @param member: The member to check the editable state for.
        @type member: str or L{Member<cocktail.schema.member.Member>}

        @return: True if the member should be displayed as a user editable
            control, False if it should be displayed as a static, unmodifiable
            piece of data.
        @rtype: bool
        """
        return self.__member_editable.get(
                    self._normalize_member(member),
                    self.editable)

    def set_member_editable(self, member, editable):
        """Determines if the given member should be editable by users. This
        affects the kind of display used by the member (for example, a text
        entry widget for an editable member, a static text label for a non
        editable one).

        @param member: The member to check the editable state for.
        @type member: str or L{Member<cocktail.schema.member.Member>}

        @param editable: True if the member should be displayed as a user
            editable control, False if it should be displayed as a static,
            unmodifiable piece of data.
        @type editable: bool
        """
        self.__member_editable[self._normalize_member(member)] = editable

    def get_member_expression(self, member):
        """Returns the expression used to obtain the value for the given
        member. If 'None' is given, values for the member will be obtained
        using regular attribute access.

        @param member: The member to get the expression for.
        @type member: str or L{Member<cocktail.schema.member.Member>}

        @return: The custom expression used to obtain the values for the
            member, if any.
        @rtype: callable
        """
        return self.__member_expressions.get(self._normalize_member(member))

    def set_member_expression(self, member, expression):
        """Sets the expression used to obtain the value for the given
        member. If 'None' is given, values for the member will be obtained
        using regular attribute access.

        @param member: The member for which the expression is set.
        @type member: str or L{Member<cocktail.schema.member.Member>}

        @param expression: The expression assigned to the member.
        @rtype: callable
        """
        self.__member_expressions[self._normalize_member(member)] = expression

    def get_member_value(self, obj, member, language = None):

        translated = member.translated
        expr = self.get_member_expression(member)

        if translated and language is None:
            language = require_language()

        if expr:
            if translated:
                return expr(obj, language)
            else:
                return expr(obj)
        else:
            accessor = self.accessor or schema.get_accessor(obj)
            value = obj
            for part in self._normalize_member(member).split("."):
                value = accessor.get(value, part, None, language)
                if value is None:
                    break
            return value

    def get_member_display(self, member):
        return self.__member_displays.get(member)

    def set_member_display(self, member, display):
        self.__member_displays[self._normalize_member(member)] = display

    def create_member_display(self, obj, member, value, **context):
        context.setdefault("persistent_object", self.persistent_object)
        return UIGenerator.create_member_display(
            self,
            obj,
            member,
            value,
            **context
        )

    def _iter_per_member_displays(
        self,
        obj,
        member,
        value,
        **context
    ):
        yield self.__member_displays.get(member)

        if member.name:
            yield getattr(self, "create_%s_display" % member.name, None)

        for display in UIGenerator._iter_per_member_displays(
            self,
            obj,
            member,
            value,
            **context
        ):
            yield display

    def translate_value(self, obj, member, value):
        return member.translate_value(value) or u"-"


NO_SELECTION = 0
SINGLE_SELECTION = 1
MULTIPLE_SELECTION = 2

class CollectionDisplay(DataDisplay):

    order = None
    sortable = True
    searchable = True
    selection_mode = NO_SELECTION
    selection = None
    grouping = None

    __user_collection = None

    def __init__(self):
        DataDisplay.__init__(self)
        self.__member_sortable = {}
        self.__member_searchable = {}
        self.__filters = []
        self.filters = ListWrapper(self.__filters)

    def get_member_sortable(self, member):
        return self.__member_sortable.get(
            self._normalize_member(member),
            self.sortable)

    def set_member_sortable(self, member, sortable):
        self.__member_sortable[self._normalize_member(member)] = sortable

    def get_member_searchable(self, member):
        return member.searchable \
            and member.user_filter \
            and self.__member_searchable.get(
                self._normalize_member,
                self.searchable
            )

    def set_member_searchable(self, member, searchable):
        self.__member_searchable[self._normalize_member(member)] = searchable

    def add_filter(self, filter):
        self.__filters.append(filter)

    def is_selected(self, item):

        if self.selection is None:
            return False
        elif self.selection_mode == SINGLE_SELECTION:
            return item == self.selection
        elif self.selection_mode == MULTIPLE_SELECTION:
            return item in self.selection

    def _get_user_collection(self):
        return self.__user_collection

    def _set_user_collection(self, collection):
        self.__user_collection = collection

        if collection:

            self.sortable = collection.allow_sorting
            self.searchable = collection.allow_filters
            self.schema = collection.schema
            self.data = collection.page_subset
            self.order = collection.order
            self.grouping = collection.grouping
            self.selection = collection.selection
            self.persistence_prefix = collection.persistence_prefix

            visible_members = collection.members

            for key in collection.schema.members():
                self.set_member_displayed(
                    key,
                    key in visible_members
                )

    user_collection = property(
        _get_user_collection,
        _set_user_collection, doc = """
        An object encapsulating a set of user provided view parameters
        (including order, pagination, visible members, etc). When set, the
        collection display will update several of its attributes to match those
        specified by the user collection.
        @type: L{UserCollection<cocktail.controllers.usercollection.UserCollection>}
        """)

