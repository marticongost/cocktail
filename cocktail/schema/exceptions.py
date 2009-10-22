#-*- coding: utf-8 -*-
u"""
Declares exception classes specific to the package.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""
from cocktail.modeling import getter


class SchemaIntegrityError(Exception):
    """Base class for all exceptions that are raised to prevent breaking the
    integrity of a schema."""


class SchemaInheritanceCycleError(Exception):
    """An exception raised when a schema tries to inherit itself, either
    directly or indirectly."""

    def __init__(self, schema):
        SchemaIntegrityError.__init__(self,
            "%s tried to use itself as an inheritance base."
        )
        self.schema = schema


class MemberRenamedError(SchemaIntegrityError):
    """An exception raised when changing the name of a schema member that is
    already bound to a schema.
    """

    def __init__(self, member, name):
        SchemaIntegrityError.__init__(self,
            "Can't rename %s to '%s'; "
            "the name of a bound schema member must remain constant."
            % (member, name)
        )
        self.member = member
        self.name = name


class MemberReacquiredError(SchemaIntegrityError):
    """An exception raised when trying to move a member between schemas."""

    def __init__(self, member, schema):
        SchemaIntegrityError.__init__(self,
            "Can't add %s to '%s'; once bound to a schema, members can't be "
            "relocated to another schema"
            % (member, schema)
        )
        self.member = member
        self.schema = schema


class ValidationError(Exception):
    """Base class for all exceptions produced during a schema validation."""

    def __init__(self, member, value, context):
        self.member = member
        self.value = value
        self.language = context.get("language")
        self.path = list(context.path())

    def __str__(self):

        desc = "%s: %s is not a valid value for %s" \
            % (self.__class__.__name__, self.value, self.member)
        
        if self.language:
            desc = "%s [%s]" % (desc, self.language)

        return desc

    @getter
    def invalid_members(self):
        """The set of members with invalid values that caused the error. This
        usually returns a list with a reference to the exception's L{member}
        attribute, but subclasses can override this property (ie. to propagate
        errors from a schema to several members that together make up a single
        concept).
        @type: L{Member<cocktail.schema.Member>} collection
        """
        return [self.member]


class ValueRequiredError(ValidationError):
    """A validation error produced when a required field is not given a
    concrete value.
    """

    def __str__(self):
        return "%s (expected a non empty value)" \
            % ValidationError.__str__(self)


class NoneRequiredError(ValidationError):
    """A validation error produced when a field that should be empty isn't."""

    def __str__(self):
        return "%s (expected an empty value)" \
            % ValidationError.__str__(self)


class TypeCheckError(ValidationError):
    """A validation error produced when a field is set to a value with a wrong
    data type.

    @ivar type: The type accepted by the field, at the time of validation.
    """

    def __init__(self, member, value, context, type):
        ValidationError.__init__(self, member, value, context)
        self.type = type

    def __str__(self):
        return "%s (expected a value of type %s, got %s instead)" % (
            ValidationError.__str__(self),
            self.type,
            type(self.value)
        )


class ClassFamilyError(ValidationError):
    """A validation error produced when a reference is set to a class that
    doesn't inherit a certain class.

    @ivar class_family: The base type that the class should inherit from, at
        the time of validation.
    """

    def __init__(self, member, value, context, class_family):
        ValidationError.__init__(self, member, value, context)
        self.class_family = class_family

    def __str__(self):
        return "%s (expected a subclass of %s, got %s instead)" % (
            ValidationError.__str__(self),
            self.class_family,
            self.value
        )

class EnumerationError(ValidationError):
    """A validation error produced when a field is set to a value that falls
    out of its set of accepted values.
    
    @ivar enumeration: The set of values accepted by the field, at the time of
        validation.
    """

    def __init__(self, member, value, context, enumeration):
        ValidationError.__init__(self, member, value, context)
        self.enumeration = enumeration

    def __str__(self):
        return "%s (should be one of %s)" \
            % (ValidationError.__str__(self), self.enumeration)


class MinLengthError(ValidationError):
    """A validation error produced when a string field is set to a value that
    doesn't reach the field's minimum length.

    @ivar max: The minimum number of characters accepted by the field, at the
        time of validation.
    @type max: int
    """

    def __init__(self, member, value, context, min):
        ValidationError.__init__(self, member, value, context)
        self.min = min

    def __str__(self):
        return "%s (should be %d or more characters long)" \
            % (ValidationError.__str__(self), self.min)


class MaxLengthError(ValidationError):
    """A validation error produced when a string field is set to a value that
    exceeds the maximum length for the field.

    @ivar max: The maximum number of characters accepted by the field, at the
        time of validation.
    @type max: int
    """

    def __init__(self, member, value, context, max):
        ValidationError.__init__(self, member, value, context)
        self.max = max

    def __str__(self):
        return "%s (can't be more than %d characters long)" \
            % (ValidationError.__str__(self), self.max)


class FormatError(ValidationError):
    """A validation error produced when a value assigned to a string field
    doesn't comply with the format mandated by the field.
    
    @ivar format: The format enforced on the field.
    @type format: Regular Expression
    """

    def __init__(self, member, value, context, format):
        ValidationError.__init__(self, member, value, context)
        self.format = format

    def __str__(self):
        return "%s (should match format %s)" \
            % (ValidationError.__str__(self), self.format)


class MinValueError(ValidationError):
    """A validation error produced when a value assigned to a scalar field
    (numbers, dates, etc) falls below a expected threshold.
    value.
    
    @ivar min: The lowest value accepted by the field, at the time of
        validation.
    """

    def __init__(self, member, value, context, min):
        ValidationError.__init__(self, member, value, context)
        self.min = min

    def __str__(self):
        return "%s (should be %s or higher)" \
            % (ValidationError.__str__(self), self.min)


class MaxValueError(ValidationError):
    """A validation error produced when a value assigned to a scalar field
    (numbers, dates, etc) exceeds a certain limit.
    
    @ivar max: The highest value accepted by the field, at the time of
        validation.
    """

    def __init__(self, member, value, context, max):
        ValidationError.__init__(self, member, value, context)
        self.max = max

    def __str__(self):
        return "%s (should be %s or lower)" \
            % (ValidationError.__str__(self), self.max)


class MinItemsError(ValidationError):
    """A validation error produced when a collection doesn't reach its minimum
    size.

    @ivar min: The minimum number of items required by the collection, at the
        time of validation.
    @type min: int
    """

    def __init__(self, member, value, context, min):
        ValidationError.__init__(self, member, value, context)
        self.min = min

    def __str__(self):
        return "%s (can't have less than %d items)" \
            % (ValidationError.__str__(self), self.min)


class MaxItemsError(ValidationError):
    """A validation error produced when a collection exceeds its maximum size.

    @ivar max: The maximum number of items allowed by the collection, at the
        time of validation.
    @type max: int
    """

    def __init__(self, member, value, context, max):
        ValidationError.__init__(self, member, value, context)
        self.max = max

    def __str__(self):
        return "%s (can't have more than %d items)" \
            % (ValidationError.__str__(self), self.max)


class RelationCycleError(ValidationError):
    """A validation error produced when a recursive relation attempts to form a
    cycle.
    """


class RelationConstraintError(ValidationError):
    """A validation error produced when a related object doesn't satisfy one of
    the constraints specified by the relation on its
    L{relation_constraints<cocktail.schema.schemarelations.RelationMember>}
    property.

    @ivar constraint: The constraint that the related object didn't fulfill.
    @type constraint: callable or L{Expression<cocktail.schema.expressions.Expression>}
    """
    
    def __init__(self, member, value, context, constraint):
        ValidationError.__init__(self, member, value, context)
        self.constraint = constraint

    def __str__(self):
        return "%s (constraint %s not satisfied)" \
            % (ValidationError.__str__(self), self.constraint)


class IntegralPartRelocationError(Exception):
    """An exception raised when trying to remove an integral part of a compound
    element to attach it to another container.
    """

