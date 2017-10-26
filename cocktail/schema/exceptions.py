#-*- coding: utf-8 -*-
u"""
Declares exception classes specific to the package.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""
from cocktail.modeling import getter
from cocktail.stringutils import decapitalize
from cocktail.translations import translations, translate_locale

translations.load_bundle("cocktail.schema.exceptions")


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

    def __init__(self, context):
        Exception.__init__(self)
        self.context = context

    @property
    def value(self):
        return self.context.value

    @property
    def member(self):
        return self.context.member

    @property
    def language(self):
        return self.context.language

    def __str__(self):

        desc = "%s: %s is not a valid value for %s" % (
            self.__class__.__name__,
            self.context.value,
            self.context.member
        )

        if self.context.language:
            desc = "%s [%s]" % (desc, self.context.language)

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

    def member_desc(self):
        return u"<em>%s</em>" % self.translate_member()

    def translate_member(self):

        from cocktail import schema

        path = list(self.context.path())
        desc = []

        for i, context in enumerate(path):
            if isinstance(context.member, schema.Schema) and (
                (i == 0 and len(path) > 1)
                or (
                    context.parent_context
                    and isinstance(
                        context.parent_context.member,
                        schema.RelationMember
                    )
                )
            ):
                continue

            label = decapitalize(translations(context.member))

            if context.collection_index is not None:
                if isinstance(context.collection_index, int):
                    label += u" %d" % (context.collection_index + 1)
                elif (
                    context.parent_context
                    and isinstance(context.parent_context.member, schema.Mapping)
                    and context.parent_context.member.keys
                ):
                    key_label = context.parent_context.member.keys.translate_value(
                        context.collection_index
                    )
                    if label:
                        if key_label:
                            label = u"%s: %s" % (key_label, label)
                    else:
                        label = key_label
                else:
                    label = u"%s: %s" % (context.collection_index, label)

            if self.language:
                label += u" (%s)" % translate_locale(self.language)

            desc.append(label.strip())

        return u" » ".join(desc)


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

    def __init__(self, context, type):
        ValidationError.__init__(self, context)
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

    def __init__(self, context, class_family):
        ValidationError.__init__(self, context)
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

    def __init__(self, context, enumeration):
        ValidationError.__init__(self, context)
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

    def __init__(self, context, min):
        ValidationError.__init__(self, context)
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

    def __init__(self, context, max):
        ValidationError.__init__(self, context)
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

    def __init__(self, context, format):
        ValidationError.__init__(self, context)
        self.format = format

    def __str__(self):
        return "%s (should match format %s)" \
            % (ValidationError.__str__(self), self.format)


class InvalidJSONError(ValidationError):
    """A validation error produced when a value assigned to a JSON field
    can't be parsed as a JSON string.
    """


class MinValueError(ValidationError):
    """A validation error produced when a value assigned to a scalar field
    (numbers, dates, etc) falls below a expected threshold.
    value.

    @ivar min: The lowest value accepted by the field, at the time of
        validation.
    """

    def __init__(self, context, min):
        ValidationError.__init__(self, context)
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

    def __init__(self, context, max):
        ValidationError.__init__(self, context)
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

    def __init__(self, context, min):
        ValidationError.__init__(self, context)
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

    def __init__(self, context, max):
        ValidationError.__init__(self, context)
        self.max = max

    def __str__(self):
        return "%s (can't have more than %d items)" \
            % (ValidationError.__str__(self), self.max)


class InternationalPhoneNumbersNotAllowedError(ValidationError):
    """A validation error produced when a phone field that doesn't accept
    international numbers validates a number containing a country prefix.
    """


class InvalidPhoneCountryError(ValidationError):
    """A validation error produced when a phone field validates a number from
    a country that is outside the subset established by
    the `cocktail.schema.phonenumber.PhoneNumber.accepted_countries` constraint.
    """


class PhoneFormatError(ValidationError):
    """A validation error produced when a phone field is set to a value that
    doesn't comply with the expected format for its country.
    """


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

    def __init__(self, context, constraint):
        ValidationError.__init__(self, context)
        self.constraint = constraint

    def __str__(self):
        return "%s (constraint %s not satisfied)" \
            % (ValidationError.__str__(self), self.constraint)


class CreditCardChecksumError(ValidationError):
    """A validation error produced for credit card numbers that have an
    invalid control digit.
    """


class IntegralPartRelocationError(Exception):
    """An exception raised when trying to remove an integral part of a compound
    element to attach it to another container.
    """


class BankAccountChecksumError(ValidationError):
    """A validation error produced for bank account numbers that have an
    invalid format.
    """
