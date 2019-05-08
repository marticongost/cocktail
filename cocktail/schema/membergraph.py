#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.schema.schema import Schema
from cocktail.schema.schemarelations import RelationMember


class MemberGraphEventInfo(EventInfo):
    path = None


class MemberGraphEventSlot(EventSlot):

    def _invoke(self, event_info):

        graph_node = event_info.target

        # Keep track of graph traversal
        if event.path is None:
            event.path = [graph_node]
        else:
            event.path.append(graph_node)

        # Invoke the event itself
        EventSlot._invoke(self, event_info)

        # Then invoke the 'modified' event (so it is triggered after any graph
        # event)
        target.modified(modification = event_info)

        # Ascend through the graph, invoking this event on any parent node,
        # recursively. Use the traversal path to prevent recursion loops.
        for parent in target.parents:
            if parent not in path:
                self.event.__get__(parent)(**kwargs)


class MemberGraphEvent(Event):
    event_info_class = MemberGraphEventInfo
    event_slot_class = MemberGraphEventSlot


class MemberGraph(object):

    _children_type = None

    modified = Event()
    object_inserted = MemberGraphEvent()
    object_deleted = MemberGraphEvent()
    object_related = MemberGraphEvent()
    object_unrelated = MemberGraphEvent()
    member_changed = MemberGraphEvent()
    translation_added = MemberGraphEvent()
    translation_deleted = MemberGraphEvent()

    def __init__(self, member, children = ()):
        self.__member = member
        self.__parents = set()
        self.__children = {}
        member._add_graph(self)
        for child in children:
            self.add(child)

    def add(self, child, replace_existing = False):

        # Select schema members by their name
        if isinstance(child, str):
            node_schema = self.schema
            if node_schema is None:
                raise ValueError(
                    "Trying to select a MemberGraph node using a member name "
                    "from a node that is not a schema, but %r."
                    % self
                )
            child = node_schema.get_member(child)
            if child is None:
                raise ValueError(
                    "Trying to select a MemberGraph node using an invalid member "
                    "name: %s" % child
                )

        # Create graph nodes to wrap member references
        if not isinstance(child, MemberGraph):
            child_type = self._children_type or self.__class__
            child = child_type(child)

        # Deal with existing nodes for the added member
        prev_child = self.__children.get(child.__member)
        if prev_child is not None:
            if replace_existing:
                prev_child.__parents.discard(self)
            else:
                return False

        self.__children[child.__member] = child
        child.__parents.add(self)
        return True

    @property
    def schema(self):
        if isinstance(self.__member, RelationMember):
            return self.__member.related_type
        if isinstance(self.__member, Schema):
            return self.__member

    @property
    def member(self):
        return self.__member

    @property
    def parents(self):
        return self.__parents

    @property
    def children(self):
        return self.__children

    def iter_members(self, include_self = False):

        if include_self:
            yield self.__member

        for child in self.__children.values():
            for descendant in child.iter_members(True):
                yield descendant

