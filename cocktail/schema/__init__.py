#-*- coding: utf-8 -*-
"""
Provides classes to describe the structure, properties and meta data of Python
data types.
"""
from cocktail.schema.member import (
    Member,
    DynamicDefault,
    NOT_EDITABLE,
    EDITABLE,
    READ_ONLY
)
from .coercion import Coercion
from cocktail.schema.schema import Schema
from .registry import (
    register_schema,
    iter_schemas,
    get_schema,
    import_type
)
from cocktail.schema.rangedmember import RangedMember
from cocktail.schema.schematuples import Tuple
from cocktail.schema.schemacollections import (
    Collection, add, remove,
    RelationCollection,
    RelationList,
    RelationSet,
    RelationOrderedSet
)
from cocktail.schema.schemamappings import (
    Mapping,
    RelationMapping
)
from cocktail.schema.schemarelations import RelationMember
from cocktail.schema.schemareference import Reference
from cocktail.schema.schemastrings import String
from cocktail.schema.schemanumbers import (
    Number,
    Integer,
    Decimal,
    Float
)
from .enumeration import Enumeration
from cocktail.schema.memberreference import MemberReference
from cocktail.schema.record import Record
from cocktail.schema.money import Money
from cocktail.schema.currency import Currency
from cocktail.schema.month import Month
from cocktail.schema.calendarpage import CalendarPage
try:
    from cocktail.schema.schemanumbers import Fraction
except ImportError:
    pass
from cocktail.schema.schemabooleans import Boolean
from cocktail.schema.schemadates import (
    BaseDateTime,
    DateTime,
    Date,
    Time
)
from cocktail.schema.url import URL
from cocktail.schema.emailaddress import EmailAddress
from cocktail.schema.phonenumber import PhoneNumber
from cocktail.schema.geocoordinates import (
    GeoCoordinate,
    Latitude,
    Longitude,
    GeoCoordinates
)
from cocktail.schema.color import Color
from cocktail.schema.creditcardnumber import CreditCardNumber
from cocktail.schema.bankaccountnumber import BankAccountNumber
from cocktail.schema.iban import IBAN
from cocktail.schema.swiftbic import SWIFTBIC
from cocktail.schema.codeblock import CodeBlock
from cocktail.schema.html import HTML
from cocktail.schema.jsonmember import JSON
from cocktail.schema.regularexpression import RegularExpression
from cocktail.schema.errorlist import ErrorList
from cocktail.schema.accessors import (
    get_accessor,
    get,
    set,
    MemberAccessor,
    AttributeAccessor,
    DictAccessor,
    undefined
)
from cocktail.schema.schemaobject import (
    SchemaObject,
    SchemaClass,
    SchemaObjectAccessor,
    TranslatedValues,
    TranslationMapping,
    translate_schema_object,
    generic_schema_object_translation,
    DO_NOT_COPY,
    SHALLOW_COPY,
    DEEP_COPY
)
from cocktail.schema.adapter import (
    reference, shallow, deep,
    Adapter,
    RuleSet,
    Rule,
    Copy,
    Exclusion,
    Split,
    Join
)
from cocktail.schema.textextractor import TextExtractor
from cocktail.schema.searchhighlighter import SearchHighlighter
from cocktail.schema.validationcontext import ValidationContext
from cocktail.schema.differences import diff

from cocktail.translations import translations
translations.load_bundle("cocktail.schema.package")

