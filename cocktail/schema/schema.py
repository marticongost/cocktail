#-*- coding: utf-8 -*-
u"""
Provides a member that handles compound values.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""
from copy import deepcopy
from cocktail.modeling import (
    empty_dict,
    empty_list,
    ListWrapper,
    DictWrapper,
    OrderedSet
)
from cocktail.events import Event
from cocktail.translations import translations
from cocktail.schema.member import Member, DynamicDefault
from cocktail.schema.accessors import get_accessor
from cocktail.schema.exceptions import SchemaIntegrityError

default = object()


class Schema(Member):
    """A data structure, made up of one or more L{members<member.Member>}.
    Schemas are themselves members, which allows them to be nested arbitrarely
    (ie. in other schemas or L{collections<schemacollections.Collection>} to
    assemble more complex compound types.

    Schemas support inheritance. All members defined by a base schema will be
    reflected on their derived schemas. This is done dynamically: new members
    added to base schemas automatically appear as members of any derived
    schema, recursively. Derived schemas can override member definitions with
    their own, simply adding a new member matching the name of a existing one.

    Schemas can use multiple inheritance; in case of conflicting member
    definitions, the one defined by the foremost base schema (as passed to the
    L{inherit} method) will take precedence.

    @ivar bases: The list of base schemas that the schema inherits from. This
        is a shallow list; to obtain the full inheritance tree, use the
        L{ascend_inheritance} method instead.
    """
    primary_member = None
    descriptive_member = None
    members_order = None
    groups_order = []
    integral = False

    member_added = Event("""
        An event triggered when a member is added to the schema.

        @ivar member: The added member.
        @type member: L{Member<cocktail.schema.Member>}
        """)

    inherited = Event("""
        An event triggered when the schema is extended by another schema.

        @ivar schema: The derived schema that extends this schema.
        @type schema: L{Schema}
        """)

    _special_copy_keys = Member._special_copy_keys | set([
        "_Schema__bases",
        "_Schema__members",
        "_declared"
    ])

    def __init__(self, *args, **kwargs):

        members = kwargs.pop("members", None)
        Member.__init__(self, *args, **kwargs)

        self.add_validation(Schema.schema_validation_rule)

        self.__bases = None
        self.bases = ListWrapper(empty_list)

        self.__members = None

        if members:
            if isinstance(members, (list, tuple)) and not self.members_order:
                self.members_order = [member.name for member in members]

            self.expand(members)

    def __deepcopy__(self, memo):
        schema_copy = Member.__deepcopy__(self, memo)

        if not isinstance(schema_copy, type):
            if self.__bases:
                for base in self.__bases:
                    schema_copy.inherit(base)

        if self.__members:
            for member in self.__members.itervalues():
                schema_copy.add_member(deepcopy(member))

        return schema_copy

    def init_instance(self,
        instance,
        values = None,
        accessor = None,
        excluded_members = None):

        if accessor is None:
            accessor = get_accessor(instance)

        # Set the value of all object members, either from a parameter or from
        # a default value definition
        for name, member in self.members().iteritems():

            if excluded_members is not None and member in excluded_members:
                continue

            value = default if values is None else values.get(name, default)

            if value is default:

                if member.translated:
                    continue

                value = member.produce_default(instance)

            accessor.set(instance, name, value)

    def produce_default(self, instance = None):
        default = Member.produce_default(self, instance)
        if default is None:
            default = self._create_default_instance()
        return default

    def _create_default_instance(self):
        if self.type:
            default = self.type()
        elif isinstance(self, type):
            default = self()
        else:
            default = {}

        self.init_instance(default)

        return default

    def inherit(self, *bases):
        """Declare an inheritance relationship towards one or more base
        schemas.

        @param bases: The list of base schemas to inherit from.
        @type bases: L{Schema}
        """

        def prevent_cycle(bases):
            for base in bases:
                if base is self:
                    raise SchemaInheritanceCycleError(self)
                if base.__bases:
                    prevent_cycle(base.__bases)

        prevent_cycle(bases)

        if self.__bases is None:
            self.__bases = []
            self.bases = ListWrapper(self.__bases)

        for base in bases:
            self.__bases.append(base)

            for ancestor in reversed(list(base.ascend_inheritance(True))):
                ancestor.inherited(schema = self)

    def ascend_inheritance(self, include_self = False):

        if include_self:
            yield self

        if self.__bases:
            for base in self.__bases:
                for ascendant in base.ascend_inheritance(True):
                    yield ascendant

    def descend_inheritance(self, include_self = False):

        if self.__bases:
            for base in self.__bases:
                for ascendant in base.descend_inheritance(True):
                    yield ascendant

        if include_self:
            yield self

    def add_member(self, member, append = False, after = None, before = None):
        """Adds a new member to the schema.

        @param member: The member to add.
        @type member: L{Member<member.Member>}

        @raise SchemaIntegrityError: Raised when trying to add an anonymous
            member to the schema. All members must have a unique name.
        """
        self._check_member(member)
        self._add_member(member)

        if append or after or before:

            if ((1 if append else 0)
              + (1 if after else 0)
              + (1 if before else 0) > 1):

                raise ValueError(
                    "Can't combine the 'append', 'after' or 'before' "
                    "parameters when calling Schema.add_member()"
                )

            if self.members_order is None:
                self.members_order = list(self.members(recursive = False))
            elif not isinstance(self.members_order, list):
                self.members_order = list(self.members_order)

            if append:
                self.members_order.append(member)
            elif after:
                pos = self.members_order.index(after)
                self.members_order.insert(pos + 1, member)
            else:
                pos = self.members_order.index(before)
                self.members_order.insert(pos, member)

        member.attached()
        self.member_added(member = member)

    def _check_member(self, member):
        if member.name is None:
            raise SchemaIntegrityError(
                "Can't add an anonymous member to %s" % self
            )

    def _add_member(self, member):
        if self.__members is None:
            self.__members = {}

        if member.primary:
            self.primary_member = member

        if member.descriptive:
            self.descriptive_member = member

        self.__members[member.name] = member
        member._schema = self

    def expand(self, members):
        """Adds several members to the schema.

        @param members: A list or mapping of additional members to add to the
            copy. When given as a mapping, the keys will be used for the member
            names.
        @type members: L{Member<member.Member>} list
            or (str, L{Member<member.Member>}) dict
        """

        # From a dictionary
        if isinstance(members, dict):
            for name, member in members.iteritems():

                if isinstance(member, type):
                    member = member()

                member.name = name
                self.add_member(member)

        # From a list
        else:
            # Use the provided list as an implicit order sequence for the
            # schema members
            if not self.members_order:
                self.members_order = [member.name for member in members]

            for member in members:
                self.add_member(member)

    def remove_member(self, member):
        """Removes a member from the schema.

        @param member: The member to remove. Can be specified using a reference
            to the member object itself, or giving its name.
        @type member: L{Member<member.Member>} or str

        @raise L{SchemaIntegrityError<exceptions.SchemaIntegrityError>}:
            Raised if the member doesn't belong to the schema.
        """

        # Normalize string references to member objects
        if isinstance(member, basestring):
            member = self[member]

        if member._schema is not self:
            raise SchemaIntegrityError(
                "Trying to remove %s from a schema it doesn't belong to (%s)"
                % (member, self)
            )

        member._schema = None
        del self.__members[member.name]

    def members(self, recursive = True):
        """A dictionary with all the members defined by the schema and its
        bases.

        @param recursive: Indicates if the returned dictionary should contain
            members defined by the schema's bases. This is the default
            behavior; Setting this parameter to False will exclude all
            inherited members.
        @type recursive: False

        @return: A mapping containing the members for the schema, indexed by
            member name.
        @rtype: (str, L{Member<members.Member>}) read only dict
        """
        if recursive and self.__bases:

            members = {}

            def descend(schema):

                if schema.__bases:
                    for base in schema.__bases:
                        descend(base)

                if schema.__members:
                    for name, member in schema.__members.iteritems():
                        members[name] = member

            descend(self)
            return DictWrapper(members)

        else:
            return DictWrapper(self.__members or empty_dict)

    def get_member(self, name):
        """Obtains one of the schema's members given its name.

        @param name: The name of the member to look for.
        @type name: str

        @return: The requested member, or None if the schema doesn't contain a
            member with the indicated name.
        @rtype: L{Member<member.Member>}
        """
        member = self.__members and self.__members.get(name)

        if member is None and self.__bases:
            for base in self.__bases:
                member = base.get_member(name)
                if member:
                    break

        return member

    def __getitem__(self, name):
        """Overrides the indexing operator to retrieve members by name.

        @param name: The name of the member to retrieve.
        @rtype name: str

        @return: A reference to the requested member.
        @rtype: L{Member<member.Member>}

        @raise KeyError: Raised if neither the schema or its bases possess a
            member with the specified name.
        """
        member = self.get_member(name)

        if member is None:
            raise KeyError("%s doesn't define a '%s' member" % (self, name))

        return member

    def __setitem__(self, name, member):
        """Overrides the indexing operator to bind members to the schema under
        the specified name.

        @param name: The name to assign to the member.
        @type name: str

        @param member: The member to add to the schema.
        @type member: L{Member<member.Member>}
        """
        member.name = name
        self.add_member(member)

    def __contains__(self, name):
        """Indicates if the schema contains a member with the given name.

        @param name: The name of the member to search for.
        @type name: str

        @return: True if the schema contains a member by the given name, False
            otherwise.
        @rtype: bool
        """
        return self.get_member(name) is not None

    def validations(self, recursive = True):
        """Iterates over all the validation rules that apply to the schema.

        @param recursive: Indicates if validations inherited from base schemas
            should be included. This is the default behavior.

        @return: The sequence of validation rules for the member.
        @rtype: callable iterable
        """
        if self.__bases:

            validations = OrderedSet()

            def descend(schema):

                if schema.__bases:
                    for base in schema.__bases:
                        descend(base)

                if schema._validations:
                    validations.extend(schema._validations)

            descend(self)
            return ListWrapper(validations)

        elif self._validations:
            return ListWrapper(self._validations)

        else:
            return empty_list

    def schema_validation_rule(self, validable, context):
        """Validation rule for schemas. Applies the validation rules defined by
        all members in the schema, propagating their errors."""

        accessor = self.accessor \
            or context.get("accessor", None) \
            or get_accessor(validable)

        context.enter(self, validable)

        try:
            for member in self.ordered_members():

                if member.translated:

                    for value in self.translated_member_values(
                        member,
                        validable,
                        context,
                        accessor):

                        for error in member.get_errors(value, context):
                            yield error
                else:
                    value = accessor.get(
                        validable,
                        member.name,
                        default = None
                    )

                    for error in member.get_errors(value, context):
                        yield error
        finally:
            context.leave()

    def translated_member_values(
        self,
        member,
        validable,
        context,
        accessor = None):

        accessor = accessor \
            or self.accessor \
            or context.get("accessor", None) \
            or get_accessor(validable)

        context_languages = context.get("languages")
        prev_language = context.get("language")
        key = member.name

        try:
            for language in (
                context_languages
                or accessor.languages(validable, key)
            ):
                context["language"] = language

                value = accessor.get(
                    validable,
                    key,
                    language = language,
                    default = None)

                yield value
        finally:
            context["language"] = prev_language

    def ordered_members(self, recursive = True):
        """Gets a list containing all the members defined by the schema, in
        order.

        Schemas can define the ordering for their members by supplying a
        L{members_order} attribute, which should contain a series of object or
        string references to members defined by the schema. Members not in that
        list will be appended at the end, sorted by name. Inherited members
        will be prepended, in the order defined by their parent schema.

        The L{Member.before_member} and L{after_member} attributes can also be
        used to alter the position of the member they are defined in.

        Alternatively, schema subclasses can override this method to allow for
        more involved sorting logic.

        @param recursive: Indicates if the returned list should contain members
            inherited from base schemas (True) or if only members directly
            defined by the schema should be included.
        @type recursive: bool

        @return: The list of members in the schema, in order.
        @rtype: L{Member<member.Member>} list
        """
        ordered = []
        relative = list()

        schemas = self.descend_inheritance(True) if recursive else (self,)

        for schema in schemas:
            if schema.__members:
                remaining = set(schema.__members.itervalues())

                if schema.members_order:
                    for member in schema.members_order:
                        if isinstance(member, basestring):
                            member = schema[member]
                        if not (member.before_member or member.after_member):
                            remaining.remove(member)
                            ordered.append(member)

                for member in list(remaining):
                    if member.before_member or member.after_member:
                        relative.append(member)
                        remaining.remove(member)

                ordered.extend(sorted(remaining, key = lambda m: m.name))

        if relative:
            def insert_relative(member, visited):
                
                # Disallow conflicting positions
                if member.before_member and member.after_member:
                    raise ValueError(
                        "Can't decide the proper order for %s, it defines "
                        "both 'before_member' and 'after_member'" % member
                    )

                # Prevent cycles
                if member not in visited:
                    visited.add(member)
                else:
                    raise ValueError(
                        "Cycle detected in the relative position for %s"
                        % member
                    )

                # Locate the 'anchor' member
                pos = -1
                anchor = member.before_member or member.after_member

                if isinstance(anchor, basestring):
                    if recursive:
                        anchor = self.get_member(anchor)
                    else:
                        anchor = self.__members.get(anchor)

                if anchor:
                    # If the anchor member is also relatively positioned,
                    # fix down its position (this works recursively)
                    if (anchor.before_member or anchor.after_member) \
                    and anchor in relative:
                        relative.remove(anchor)
                        pos = insert_relative(anchor, visited)
                    else:
                        pos = ordered.index(anchor)

                # Insert the member
                if pos == -1:
                    pos = len(ordered)
                elif member.after_member:
                    pos += 1

                ordered.insert(pos, member)
                return pos

            while relative:
                insert_relative(relative.pop(0), set())

        return ordered

    def ordered_groups(self, recursive = True):
        """Gets a list containing all the member groups defined by the schema,
        in order.

        @param recursive: Indicates if the returned list should contain groups
            defined by base schemas.
        @type recursive: bool

        @return: The list of groups defined by the schema, in order.
        @rtype: str list
        """
        ordered_groups = []
        visited = set()

        def collect(schema):
            if schema.groups_order:
                for group in schema.groups_order:
                    if group not in visited:
                        visited.add(group)
                        ordered_groups.append(group)

            for member in schema.ordered_members(recursive = False):
                group = member.member_group
                if group and group not in visited:
                    visited.add(group)
                    ordered_groups.append(group)

            if recursive:
                if schema.__bases:
                    for base in schema.__bases:
                        collect(base)

        collect(self)
        return ordered_groups

    def grouped_members(self, recursive = True):
        """Returns the groups of members defined by the schema.

        @param recursive: Indicates if the returned list should contain members
            inherited from base schemas (True) or if only members directly
            defined by the schema should be included.
        @type recursive: bool

        @return: A list of groups in the schema and their members, in order.
            Each group is represented with a tuple containing its name and the
            list of its members.
        @rtype: list(tuple(str, L{Member<cocktail.schema.member.Member>} sequence))
        """
        members_by_group = {}

        for member in self.ordered_members(recursive):
            group_members = members_by_group.get(member.member_group)
            if group_members is None:
                group_members = []
                members_by_group[member.member_group] = group_members
            group_members.append(member)

        groups = []

        for group_name in self.ordered_groups(recursive):
            group_members = members_by_group.get(group_name)
            if group_members:
                groups.append((group_name, group_members))

        ungroupped_members = members_by_group.get(None)
        if ungroupped_members:
            groups.insert(0, (None, ungroupped_members))

        return groups

    def translate_group(self, group):

        def get_label(schema):
            if not isinstance(schema, Schema):
                return None

            if schema.name:
                label = translations(schema.name + "." + group)
                if label:
                    return label

            for base in schema.bases:
                label = get_label(base)
                if label:
                    return label

        label = get_label(self)
        
        if label:
            return label
        
        if self.adaptation_source is not None:
            label = get_label(self.adaptation_source)

        return label

    def insert_group(self, group, before = None, after = None):

        if before is None and after is None:
            raise ValueError(
                "insert_group() requires a value for either the 'after' or "
                "'before' parameters"
            )
        elif before is not None and after is not None:
            raise ValueError(
                "insert_group() can't take both 'after' and 'before' "
                "parameters at the same time"
            )
 
        anchor = before or after
        if not isinstance(self.groups_order, list):
            self.groups_order = list(self.groups_order)

        try:
            pos = self.groups_order.index(anchor)
        except ValueError:
            self.groups_order.append(group)
        else:
            if after:
                pos += 1
            self.groups_order.insert(pos, group)

