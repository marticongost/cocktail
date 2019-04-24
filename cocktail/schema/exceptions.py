#-*- coding: utf-8 -*-
"""
Declares exception classes specific to the package.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""
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
        super().__init__(
            f"{schema} tried to use itself as an inheritance base."
        )
        self.schema = schema


class MemberRenamedError(SchemaIntegrityError):
    """An exception raised when changing the name of a schema member that is
    already bound to a schema.
    """

    def __init__(self, member, name):
        super.__init__(
            f"Can't rename {member} to '{name}'; "
            "the name of a bound schema member must remain constant."
        )
        self.member = member
        self.name = name


class MemberReacquiredError(SchemaIntegrityError):
    """An exception raised when trying to move a member between schemas."""

    def __init__(self, member, schema):
        super().__init__(
            f"Can't add {member} to {schema}; once bound to a schema, "
            "members can't be relocated to another schema"
            % (member, schema)
        )
        self.member = member
        self.schema = schema


class InputError(Exception):
    """An exception raised by `cocktail.schema.Member.coerce` when trying to
    coerce an invalid value with a `cocktail.schema.Coercion.FAIL` policy.
    """

    def __init__(self, member, value, errors):
        super().__init__(f"{value} doesn't conform to {member} ({errors})")
        self.member = member
        self.value = value
        self.errors = errors


class ValidationError(Exception):
    """Base class for all exceptions produced during a schema validation."""

    default_reason: str = None

    def __init__(self, context, reason=None):

        desc = (
            f"{self.__class__.__name__}: "
            f"{context.value} is not a valid value for {context.member}"
        )

        if context.language:
            desc += f"[{self.context.language}]"

        reason = reason or self.default_reason
        if reason:
            desc += f" ({reason})"

        super().__init__(desc)
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

    @property
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
        return "<em>%s</em>" % self.translate_member()

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
                    label += " %d" % (context.collection_index + 1)
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
                            label = "%s: %s" % (key_label, label)
                    else:
                        label = key_label
                else:
                    label = "%s: %s" % (context.collection_index, label)

            if self.language:
                label += " (%s)" % translate_locale(self.language)

            desc.append(label.strip())

        return " » ".join(desc)


class ValueRequiredError(ValidationError):
    """A validation error produced when a required field is not given a
    concrete value.
    """

    default_reason = "expected a non empty value"


class NoneRequiredError(ValidationError):
    """A validation error produced when a field that should be empty isn't."""

    default_reason = "expected an empty value"


class TypeCheckError(ValidationError):
    """A validation error produced when a field is set to a value with a wrong
    data type.

    @ivar type: The type accepted by the field, at the time of validation.
    """

    def __init__(self, context, type, reason=None):
        super().__init__(
            context,
            reason or (
                f"expected a value of type {type}, "
                f"got {type(context.value)} instead"
            )
        )
        self.type = type


class ClassFamilyError(ValidationError):
    """A validation error produced when a reference is set to a class that
    doesn't inherit a certain class.

    @ivar class_family: The base type that the class should inherit from, at
        the time of validation.
    """

    def __init__(self, context, class_family, reason=None):
        super().__init__(
            context,
            reason or f"expected a subclass of {class_family}"
        )
        self.class_family = class_family


class EnumerationError(ValidationError):
    """A validation error produced when a field is set to a value that falls
    out of its set of accepted values.

    @ivar enumeration: The set of values accepted by the field, at the time of
        validation.
    """

    def __init__(self, context, enumeration, reason=None):
        super().__init__(
            context,
            f"should be one of {enumeration}"
        )
        self.enumeration = enumeration


class MinLengthError(ValidationError):
    """A validation error produced when a string field is set to a value that
    doesn't reach the field's minimum length.

    @ivar max: The minimum number of characters accepted by the field, at the
        time of validation.
    @type max: int
    """

    def __init__(self, context, min, reason=None):
        super().__init__(
            context,
            reason or f"should be at least {min} characters long"
        )
        self.min = min


class MaxLengthError(ValidationError):
    """A validation error produced when a string field is set to a value that
    exceeds the maximum length for the field.

    @ivar max: The maximum number of characters accepted by the field, at the
        time of validation.
    @type max: int
    """

    def __init__(self, context, max, reason=None):
        super().__init__(
            context,
            reason or f"can't be more than {max} characters long"
        )
        self.max = max


class FormatError(ValidationError):
    """A validation error produced when a value assigned to a string field
    doesn't comply with the format mandated by the field.

    @ivar format: The format enforced on the field.
    @type format: Regular Expression
    """

    def __init__(self, context, format, reason=None):
        super().__init__(
            context,
            reason or f"should match format {format}"
        )
        self.format = format


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

    def __init__(self, context, min, reason=None):
        super().__init__(
            context,
            reason or f"should be {min} or higher"
        )
        self.min = min


class MaxValueError(ValidationError):
    """A validation error produced when a value assigned to a scalar field
    (numbers, dates, etc) exceeds a certain limit.

    @ivar max: The highest value accepted by the field, at the time of
        validation.
    """

    def __init__(self, context, max, reason=None):
        super().__init__(
            context,
            reason or f"should be {max} or lower"
        )
        self.max = max


class MinItemsError(ValidationError):
    """A validation error produced when a collection doesn't reach its minimum
    size.

    @ivar min: The minimum number of items required by the collection, at the
        time of validation.
    @type min: int
    """

    def __init__(self, context, min, reason=None):
        super().__init__(
            context,
            reason or f"can't have fewer than {min} items"
        )
        self.min = min


class MaxItemsError(ValidationError):
    """A validation error produced when a collection exceeds its maximum size.

    @ivar max: The maximum number of items allowed by the collection, at the
        time of validation.
    @type max: int
    """

    def __init__(self, context, max, reason=None):
        super().__init__(
            context,
            reason or f"can't have more than {max} items"
        )
        self.max = max


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

    def __init__(self, context, constraint, reason=None):
        super().__init__(
            context,
            reason or f"constraint {self.constraint} not satisfied"
        )
        self.constraint = constraint


class CreditCardChecksumError(ValidationError):
    """A validation error produced for credit card numbers that have an
    invalid control digit.
    """


class BankAccountChecksumError(ValidationError):
    """A validation error produced for bank account numbers that have an
    invalid format.
    """

