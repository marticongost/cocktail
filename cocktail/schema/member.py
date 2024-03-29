#-*- coding: utf-8 -*-
"""
Provides the base class for all schema members.
"""
from itertools import chain
from copy import deepcopy
from warnings import warn
from typing import Any
from cocktail.events import Event
from cocktail.modeling import ListWrapper, OrderedSet
from cocktail.pkgutils import get_full_name
from cocktail.translations import translations
from cocktail.schema import exceptions
from cocktail.schema.expressions import Expression, Variable
from cocktail.schema.validationcontext import ValidationContext
from cocktail.schema.accessors import get_accessor
from .coercion import Coercion
from .exceptions import InputError
from .registry import import_type

NOT_EDITABLE = 0
EDITABLE = 1
READ_ONLY = 2


class Member(Variable):
    """A member describes the properties and metadata of a unit of data.

    Although not strictly an abstract class, the class is very generic in
    nature, and is inherited by a wealth of other classes that add the
    necessary features to describe a variety of more concrete data types
    (`String`, `Integer`, `Boolean`, etc.).

    Members can also be composited, in order to describe parts of a more complex
    data set, by embedding them within a `Collection` or `Schema`.

    .. attribute:: default

        The default value for the member.

    .. attribute:: required

        Determines if the field requires a value. When set to true, a value of
        None for this member will trigger a validation error of type
        `exceptions.ValueRequiredError`.

    .. attribute:: require_none

        Determines if the field disallows any value other than None.  When set
        to true, a value different than None for this member will trigger a
        validation error of type `exceptions.NoneRequiredError`.

    .. attribute:: enumeration

        Establishes a limited set of acceptable values for the member. If a
        member with this constraint is given a value not found inside the set,
        an `exceptions.EnumerationError` error will be triggered.

    .. attribute:: translated

        Indicates if the member accepts multiple values, each in a different
        language.

    .. attribute:: expression

        An expression used by computed fields to produce their value.
    """

    attached = Event(
        doc = """An event triggered when the member is added to a schema."""
    )

    validating = Event(
        doc = """An event triggered when a validation of the member begins.

        The main purpose of this event is to modify the parameters of its
        validation context. To implement actual validation rules, check out the
        `_default_validation` and `add_validation` methods.

        :param context: The validation context representing the validation
            process that is about to start.
        """
    )

    # Groupping and sorting
    member_group = None
    before_member = None
    after_member = None

    # Constraints and behavior
    primary = False
    descriptive = False
    default = None
    required = False
    require_none = False
    enumeration = None
    normalization = None
    expression = None

    # Instance data layout
    accessor = None

    # Copying and adaptation
    _copy_class = None
    source_member = None
    original_member = None
    copy_mode = None

    # Translation
    translated = False
    translation = None
    translation_source = None
    translatable_values = False
    translatable_enumeration = False
    custom_translation_key = None

    # Wether the member is included in full text searches
    text_search = False
    __language_dependant = None

    # Attributes that deserve special treatment when performing a deep copy
    _special_copy_keys = set([
        "__module__",
        "__class__",
        "_schema",
        "_validations_wrapper",
        "_validations",
        "translation",
        "translation_source",
        "original_member",
        "source_member"
    ])

    def __init__(self, name = None, doc = None, **kwargs):
        """Initializes a member, optionally setting its name, docstring and a
        set of arbitrary attributes.

        :param name: The `name` given to the member.
        :type name: str

        :param doc: The docstring to assign to the member.
        :type doc: unicode

        :param kwargs: A set of key/value pairs to set as attributes of the
            member.
        """
        self._name = None
        self._schema = None
        self._validations = OrderedSet()
        self._validations_wrapper = ListWrapper(self._validations)
        self.original_member = self
        self.validation_parameters = {}

        Variable.__init__(self, None)
        self.__type = None

        self.name = name
        self.__doc__ = doc

        validations = kwargs.pop("validations", None)

        for key, value in kwargs.items():
            setattr(self, key, value)

        if validations is not None:
            for validation in validations:
                self.add_validation(validation)

    def __hash__(self):
        return object.__hash__(self)

    def __eq__(self, other):
        return self is other

    def __repr__(self):

        member_desc = self.__class__.__name__
        if (
            self.__class__.__module__
            and not self.__class__.__module__.startswith("cocktail.schema.")
        ):
            member_desc = self.__class__.__module__ + "." + member_desc

        return member_desc + " <%s>" % self.get_qualified_name()

    def _get_name(self):
        return self._name

    def _set_name(self, value):

        if self._schema is not None:
            raise exceptions.MemberRenamedError(self, value)

        self._name = value

    name = property(_get_name, _set_name, doc =
        """The name that uniquely identifies the member on the schema it is
        bound to. Once set it can't be changed (trying to do so will raise a
        `exceptions.MemberRenamedError` exception).
        """)

    def get_qualified_name(self, delimiter = ".", include_ns = False):
        member = self
        names = []
        while True:
            if member._name:
                names.append(member._name)
            owner = member._schema
            if owner is None:
                if include_ns:
                    namespace = getattr(member, "__module__", None)
                    if (
                        namespace
                        and not namespace.startswith("cocktail.schema.")
                    ):
                        names.append(namespace)
                break
            else:
                member = owner
        names.reverse()
        return delimiter.join(names)

    def _get_schema(self):
        return self._schema

    def _set_schema(self, value):

        if self._schema is not None:
            raise exceptions.MemberReacquiredError(self, value)

        self._schema = value

    schema = property(_get_schema, _set_schema, doc =
        """The `schema <Schema>` that the member is bound to. Once set it can't
        be changed (doing so will raise a `exceptions.MemberReacquiredError`
        exception).
        """)

    def _get_type(self):

        # Resolve string references
        if isinstance(self.__type, str):
            self.__type = import_type(self.__type)

        return self.__type

    def _set_type(self, type):
        self.__type = type

    type = property(_get_type, _set_type, doc =
        """Imposes a data type constraint on the member. All values assigned to
        this member must be instances of the specified data type. Breaking this
        restriction will produce a validation error of type
        `exceptions.TypeCheckError`.

        The value for this constraint can take either a reference to a type
        object or a fully qualified python name. When set using a name, the
        indicated type will be imported lazily, the first time the value for
        this constraint is requested. This can be helpful in avoiding circular
        references between schemas.
        """)

    def _set_exclusive(self, expr):
        self.required = expr

        if isinstance(expr, Expression):
            self.require_none = expr.not_()
        else:
            self.require_none = lambda ctx: not expr(ctx)

    exclusive = property(None, _set_exclusive, doc =
        """A write only property that eases the definition of members that
        should be required or empty depending on a condition and its negation,
        respectively.

        Should be set to a dynamic expression (a callable object, or an
        instance of `expressions.Expression`).
        """)

    def produce_default(self, instance = None):
        """Generates a default value for the member. Can be overridden (ie. to
        produce dynamic default values).

        :param instance: The instance that the default is produced for.

        :return: The resulting default value.
        """
        if instance is not None and self.name:
            default = getattr(instance, "default_" + self.name, self.default)
        else:
            default = self.default

        if isinstance(default, DynamicDefault):
            default = default()

        return self.normalization(default) if self.normalization else default

    def copy(self, **kwargs):
        """Creates a deep, unbound copy of the member.

        Keyword arguments are assigned as attributes of the new member. It is
        possible to use dotted names to set attributes of nested objects.
        """
        member_copy = self.__deepcopy__({})

        # Set 'primary' before any other property, to avoid constraint
        # violations (f. eg. setting required = False, primary = False would
        # fail if the 'required' property was set first)
        primary = kwargs.pop("primary", None)
        if primary is not None:
            member_copy.primary = primary

        for key, value in kwargs.items():
            obj = member_copy

            name_parts = key.split(".")

            for name in name_parts[:-1]:
                obj = getattr(obj, name)

            setattr(obj, name_parts[-1], value)

        return member_copy

    def __deepcopy__(self, memo):

        # Custom class
        if self._copy_class:
            copy = self._copy_class()

        # Copying a SchemaObject
        elif issubclass(self.__class__, type):
            members = self.members()
            copy = self.__class__(self.name, self.__bases__, dict(
                (key, value)
                for key, value in self.__dict__.items()
                if key not in self._special_copy_keys
                and key not in members
            ))

        # Regular copy
        else:
            copy = self.__class__()

        memo[id(self)] = copy

        if not isinstance(copy, type):
            for key, value in self.__dict__.items():
                if key not in self._special_copy_keys:
                    copy.__dict__[key] = deepcopy(value, memo)

        copy._validations = list(self._validations)
        memo[id(self._validations)] = copy._validations

        copy._validations_wrapper = ListWrapper(copy._validations)
        memo[id(copy._validations_wrapper)] = copy._validations_wrapper

        copy.source_member = self
        copy.original_member = self.original_member

        return copy

    def detach_from_source_member(self):
        self.source_member = None
        self.original_member = self

    def add_validation(self, validation):
        """Adds a validation function to the member.

        :param validation: A callable that will be added as a validation rule
            for the member. Takes a single positional parameter (a reference to
            a `ValidationContext` object). The callable should produce a sequence
            of `exceptions.ValidationError` instances.
        :type validation: callable

        :return: The validation rule, as provided.
        :rtype: callable
        """
        self._validations.append(validation)
        return validation

    def remove_validation(self, validation):
        """Removes one of the validation rules previously added to a member.

        :param validation: The validation to remove, as previously passed to
            `add_validation`.
        :type validation: callable

        :raise ValueError: Raised if the member doesn't have the indicated
            validation.
        """
        self._validations.remove(validation)

    def validations(self, recursive = True, **validation_parameters):
        """Iterates over all the validation rules that apply to the member.

        :param recursive: Indicates if the produced set of validations should
            include those declared on members contained within the member. This
            parameter is only meaningful on compound members, but is made
            available globally in order to allow the method to be called
            polymorphically using a consistent signature.
        :type recursive: bool

        :return: The sequence of validation rules for the member.
        :rtype: callable iterable
        """
        return self._validations_wrapper

    def validate(self, value, **validation_parameters):
        """Indicates if the given value fulfills all the validation rules
        imposed by the member.

        :param value: The value to validate.

        :param validation_parameters: Additional parameters used to initialize
            the `ValidationContext` instance generated by this validation
            process.
        :type validation_parameters: `ValidationContext`

        :return: True if the given value satisfies the validations imposed by
            this member, False otherwise.
        :rtype: bool
        """
        for error in self.get_errors(value, **validation_parameters):
            return False

        return True

    def get_errors(self, value, **validation_parameters):
        """Tests the given value with all the validation rules declared by the
        member, iterating over the resulting set of errors.

        :param value: The value to evaluate.

        :param validation_parameters: Additional parameters used to initialize
            the `ValidationContext` instance generated by this validation
            process.
        :type validation_parameters: `ValidationContext`

        :return: An iterable sequence of validation errors.
        :rtype: `exceptions.ValidationError` iterable
        """
        context = ValidationContext(self, value, **validation_parameters)

        for error in self._default_validation(context):
            yield error

        for validation in self.validations(**validation_parameters):
            for error in validation(context):
                yield error

    def coerce(
            self,
            value: Any,
            coercion: Coercion,
            **validation_parameters) -> Any:
        """Coerces the given value to conform to the member definition.

        The method applies the behavior indicated by the `coercion` parameter,
        either accepting or rejecting the given value. Depending on the
        selected coercion strategy, rejected values may be transformed into a
        new value or raise an exception.

        New values are both modified in place (when possible) and returned.
        """
        if coercion is Coercion.NONE:
            return value

        errors = self.get_errors(value, **validation_parameters)

        if coercion is Coercion.FAIL:
            errors = list(errors)
            if errors:
                raise InputError(self, value, errors)
        else:
            for error in errors:
                if coercion is Coercion.FAIL_IMMEDIATELY:
                    raise InputError(self, value, [error])
                elif coercion is Coercion.SET_NONE:
                    return None
                elif coercion is Coercion.SET_DEFAULT:
                    return self.produce_default()

        return value

    @classmethod
    def resolve_constraint(cls, expr, context):
        """Resolves a constraint expression for the given context.

        Most constraints can be specified using dynamic expressions instead of
        static values, allowing them to adapt to different validation contexts.
        For example, a field may state that it should be required only if
        another field is set to a certain value. This method normalizes any
        constraint (either static or dynamic) to a static value, given a
        certain validation context.

        Dynamic expressions are formed by assigning a callable object or an
        `expressions.Expression` instance to a constraint value.

        :param expr: The constraint expression to resolve.

        :param context: The validation context that will be made available to
            dynamic constraint expressions.
        :type context: `ValidationContext`

        :return: The normalized expression value.
        """
        if not isinstance(expr, type):
            if isinstance(expr, Expression):
                return expr.eval(
                    context.get_object(-2)
                    if context.parent_context
                    else None
                )
            elif callable(expr):
                return expr(context)

        return expr

    def _default_validation(self, context):
        """A method implementing the intrinsic validation rules for a member.

        Each member subtype should extend this method to implement its
        constraints and validation rules.

        :param context: The validation context to evaluate.
        :type context: `ValidationContext`

        :return: An iterable sequence of validation errors.
        :rtype: `exceptions.ValidationError` iterable
        """
        # Value required
        if context.value is None:
            if self.resolve_constraint(self.required, context):
                yield exceptions.ValueRequiredError(context)

        # None required
        elif self.resolve_constraint(self.require_none, context):
            yield exceptions.NoneRequiredError(context)

        else:
            # Enumeration
            enumeration = self.resolve_constraint(self.enumeration, context)

            if enumeration is not None and context.value not in enumeration:
                yield exceptions.EnumerationError(context, enumeration)

            # Type check
            type = self.resolve_constraint(self.type, context)

            if type and not isinstance(context.value, type):
                yield exceptions.TypeCheckError(context, type)

    def get_possible_values(self, context = None):
        if self.enumeration is not None:
            if context is None:
                context = ValidationContext(self, None)
            enumeration = self.resolve_constraint(
                self.enumeration,
                context
            )
            if enumeration:
                return enumeration

    def translate_value(self, value, language = None, **kwargs):
        if value is None:
            return translations(
                self,
                language = language,
                suffix = ".none",
                **kwargs
            )
        elif (
            (value or value == 0)
            and self.translatable_values or (
                self.translatable_enumeration
                and self.enumeration
            )
        ):
            return translations(
                self,
                language = language,
                suffix = ".values.%s" % value
            )
        else:
            return str(value)

    def translate_error(self, error, language = None, **kwargs):

        for error_class in error.__class__.__mro__:

            try:
                error_class_name = get_full_name(error.__class__)
            except Exception as ex:
                error_class_name = error.__class__.__name__

            error_translation = translations(
                self,
                suffix = ".errors." + error_class_name,
                error = error,
                language = language
            )
            if error_translation:
                return error_translation

        # No custom translation for the error, return the stock description
        return translations(error, language = language, **kwargs)

    def get_member_explanation(self, language = None, **kwargs):
        return translations(
            self,
            language = language,
            suffix = ".explanation",
            **kwargs
        )

    def _get_language_dependant(self):
        explicit_state = self.__language_dependant
        return (
            self._infer_is_language_dependant()
            if explicit_state is None
            else explicit_state
        )

    def _set_language_dependant(self, value):
        self.__language_dependant = value

    def _infer_is_language_dependant(self):
        return (
            self.translated
            or (
                self.translatable_enumeration
                and self.enumeration is not None
            )
        )

    language_dependant = property(
        _get_language_dependant,
        _set_language_dependant
    )

    def extract_searchable_text(self, extractor):
        extractor.feed(
            self.translate_value(
                extractor.current.value,
                language = extractor.current.language
            )
        )

    __editable = None

    def _get_editable(self):

        if self.__editable is None:
            if self.expression is None:
                return EDITABLE
            else:
                return READ_ONLY

        return self.__editable

    def _set_editable(self, editable):
        if isinstance(editable, bool):
            warn(
                "Setting Member.editable to a bool is deprecated, use one of "
                "schema.EDITABLE, schema.NOT_EDITABLE or schema.READ_ONLY",
                DeprecationWarning,
                stacklevel = 2
            )
            editable = EDITABLE if editable else NOT_EDITABLE
        self.__editable = editable

    editable = property(_get_editable, _set_editable)

    def to_json_value(self, value, **options):
        return value

    def from_json_value(self, value, **options):
        return value

    def serialize(self, value: Any, **options) -> str:
        return str(value)

    def parse(self, value: str, **options) -> Any:

        if not value.strip():
            return None

        if self.type:
            return self.type(value)
        else:
            return value

    def resolve_expression(self, obj, language=None):
        expression = self.expression
        if getattr(expression, "__self__", None) is obj:
            if self.translated:
                return expression(obj, language)
            else:
                return expression(obj)
        else:
            if self.translated:
                return expression(self, obj, language)
            else:
                return expression(self, obj)


class DynamicDefault(object):

    def __init__(self, factory):
        self.factory = factory

    def __call__(self):
        return self.factory()


@translations.instances_of(Member)
def translate_member(
    member,
    suffix = "",
    qualified = False,
    include_type_default = True,
    **kwargs
):
    if qualified:
        return translations("cocktail.schema.qualified_member", member = member)

    if suffix is None:
        suffix = ""

    if member.custom_translation_key:
        translation = translations(
            member.custom_translation_key + suffix,
            member = member,
            **kwargs
        )
        if translation:
            return translation

    if member.schema:

        if member.name:
            schema_name = getattr(
                member.schema,
                "full_name",
                member.schema.name
            )
            if schema_name:
                key = (
                    schema_name
                    + ".members."
                    + member.name
                    + suffix
                )
                translation = translations(
                    key,
                    member = member,
                    **kwargs
                )
                if translation:
                    return translation

        for schema_alias in member.schema.schema_aliases:
            key = (
                schema_alias
                + ".members."
                + member.name
                + suffix
            )
            translation = translations(
                key,
                member = member,
                **kwargs
            )
            if translation:
                return translation

    if member.source_member:
        translation = translations(
            member.source_member,
            suffix = suffix,
            include_type_default = False,
            **kwargs
        )
        if translation:
            return translation

    if include_type_default:
        for member_type in member.__class__.__mro__:
            if issubclass(member_type, Member):
                translation = translations(
                    get_full_name(member_type)
                        + ".default_member_translation"
                        + suffix,
                    member = member,
                    **kwargs
                )
                if translation:
                    return translation

    return None

