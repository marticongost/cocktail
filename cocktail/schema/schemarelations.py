#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from threading import local
from cocktail.modeling import getter, abstractmethod
from cocktail.schema.accessors import get
from cocktail.schema.member import Member
from cocktail.schema.expressions import Expression
from cocktail.schema.exceptions import (
    SchemaIntegrityError, IntegralPartRelocationError
)

_thread_data = local()

def _update_relation(action, obj, related_obj, member, relocation = False):

    if action == "relate":
        method = member.related_end.add_relation
    elif action == "unrelate":
        method = member.related_end.remove_relation

        # Don't allow items bound to an integral relation to be relocated to a
        # new container
        if relocation and member.bidirectional and member.related_end.integral:
            if get(obj, member) is not None:
                raise IntegralPartRelocationError()
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
    """Base class for all members that describe a single end of a relation
    between two or more schemas.
    
    This is an abstract class; Noteworthy concrete subclasses include
    L{Reference<cocktail.schema.schemareference.Reference>} and
    L{Collection<cocktail.schema.schemacollections.Collection>}.

    @ivar relation_constraints: A collection of constraints imposed on related
        items during validation. Constraints can be specified using schema
        expressions or a callable. Expressions are evaluated normally using the
        related object as the context. Callables receive the relation owner and
        a related object as a parameter. Both types of constraints should
        evaluate to True if the related object satisfies their requirements, or
        False otherwise.

        During validation, a failed relation constraint will produce a
        L{RelationConstraintError<cocktail.schemas.exceptions.RelationConstraintError>}
        exception.

    @type relation_constraints: collection of callables or
        L{Expression<cocktail.schema.expressions.Expression>} instances
    """
    bidirectional = False
    integral = False
    related_key = None
    relation_constraints = None
    _many = False
    __related_end = None

    def __init__(self, *args, **kwargs):
        Member.__init__(self, *args, **kwargs)

        if self.integral and not self.bidirectional:
            raise SchemaIntegrityError(
                "%s can't be declared 'integral' without setting "
                "'bidirectional' to True" % self)

    @getter
    def related_end(self):
        """Gets the opposite end of a bidirectional relation.
        @type: L{Member<member.Member>}
        """    
        if self.__related_end:
            return self.__related_end
        
        if not self.bidirectional:
            return None

        related_end = None
        related_type = self.related_type

        if self.related_key:
            related_end = related_type.get_member(self.related_key)

            if not getattr(related_end, "bidirectional", False) \
            or (
                related_end.related_key
                and related_end.related_key != self.name
            ):
                related_end = None
        else:
            for member in related_type.members().itervalues():
                if getattr(member, "bidirectional", False):
                    if member.related_key:
                        if self.name == member.related_key:
                            related_end = member
                            break
                    elif self.schema is member.related_type \
                    and member is not self:
                        related_end = member
                        break
        
        # Related end missing
        if related_end is None:
            raise SchemaIntegrityError(
                "Couldn't find the related end for %s" % self
            )
        # Disallow relations were both ends are declared as integral
        elif self.integral and related_end.integral:
            raise SchemaIntegrityError(
                "Can't declare both ends of a relation as integral (%s <-> %s)"
                % (self, related_end)
            )
        # Disallow integral many to many relations
        elif (self.integral or related_end.integral) \
        and (self._many and related_end._many):
            raise SchemaIntegrityError(
                "Can't declare a many to many relation as integral (%s <-> %s)"
                % (self, related_end)
            )

        self.__related_end = related_end 
        return related_end

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

    def validate_relation_constraint(self, constraint, owner, related):

        # Expression-based constraint
        if isinstance(constraint, Expression):
            return constraint.eval(related)

        # Callable-based constraint
        elif callable(constraint):
            return constraint(owner, related)

        # Unknown constraint type
        else:
            raise TypeError(
                "%s is not a valid relation constraint; "
                "expected a callable or an Expression instance"
                % constraint
            )

