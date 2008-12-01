#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from threading import local
from cocktail.modeling import getter, abstractmethod
from cocktail.schema.member import Member

_thread_data = local()

def _update_relation(action, obj, related_obj, member):

    if action == "relate":
        method = member.related_end.add_relation
    elif action == "unrelate":
        method = member.related_end.remove_relation
    else:
        raise ValueError("Unknown relation action: %s" % action)

    pushed = _push(action, obj, related_obj, member)

    try:
        method(related_obj, obj)
    finally:
        if pushed:
            _pop()

def _push(action, obj, related_obj, member):
    
    stack = getattr(_thread_data, "stack", None)

    if stack is None:
        stack = []
        _thread_data.stack = stack

    entry = (action, obj, related_obj, member)

    if entry not in stack:
        stack.append(entry)
        return True
    else:
        return False

def _pop():

    stack = getattr(_thread_data, "stack", None)

    if not stack:
        raise ValueError(
            "The relation stack is empty, can't pop its last entry")

    entry = stack.pop()
    return entry


class RelationMember(Member):

    bidirectional = False
    related_key = None
    __related_end = None

    @getter
    def related_end(self):
        """Gets the opposite end of a bidirectional relation.
        @type: L{Member<member.Member>}
        """    
        if self.__related_end:
            return self.__related_end
        
        member = None
        related_type = self.related_type

        if self.related_key:
            member = related_type[self.related_key]

            if not getattr(member, "bidirectional", False) \
            or (member.related_key and member.related_key != self.name):
                member = None
        else:
            for member in related_type.members().itervalues():
                if getattr(member, "bidirectional", False):
                    if member.related_key:
                        if self.name == member.related_key:
                            break
                    elif self.schema is member.related_type:
                        break
        
        if member is None:
            raise TypeError("Couldn't find the related end for %s" % self)
        
        self.__related_end = member
        return member

    @getter
    @abstractmethod
    def related_type(self):
        pass

    def add_relation(self, obj, related_obj):
        if _push("relate", obj, related_obj, self):
            try:
                self._add_relation(obj, related_obj)
            finally:
                _pop()

    def remove_relation(self, obj, related_obj):
        if _push("unrelate", obj, related_obj, self):
            try:
                self._remove_relation(obj, related_obj)
            finally:
                _pop()

