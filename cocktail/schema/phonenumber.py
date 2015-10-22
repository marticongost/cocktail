#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from string import digits
from cocktail.schema.schemastrings import String
from cocktail.schema.exceptions import (
    InternationalPhoneNumbersNotAllowedError,
    InvalidPhoneCountryError,
    PhoneFormatError
)

NINE_DIGITS_EXPR = re.compile(r"^\d{9}$")


class PhoneNumber(String):

    prefix_normalization = None
    international_numbers = "accept"
    accepted_countries = None
    local_country = None

    __countries_by_prefix = {}
    __prefixes_by_country = {}
    __country_formats = {}

    @classmethod
    def get_country_from_prefix(cls, prefix):
        return cls.__countries_by_prefix.get(prefix)

    @classmethod
    def get_prefix_for_country(cls, country):
        return cls.__prefixes_by_country.get(country)

    @classmethod
    def get_country_format(cls, country):
        return cls.__country_formats.get(country)

    @classmethod
    def set_country_info(cls, country, prefix, format):
        cls.__countries_by_prefix[prefix] = country
        cls.__prefixes_by_country[country] = prefix
        cls.__country_formats[country] = format

    def normalization(self, value):

        if value:

            value = value.replace("(", " ")
            value = value.replace(")", " ")
            value = value.strip()

            if value.startswith("00"):
                value = value[2:].lstrip()

            if value.startswith("+"):
                try:
                    prefix, number = value.split(" ", 1)
                    prefix = int(prefix)
                except:
                    number = value
                    prefix = None
                else:
                    if (
                        self.prefix_normalization == "strip_local"
                        and self.local_country
                        and self.get_country_from_prefix(prefix)
                           == self.local_country
                    ):
                        prefix = None
            else:
                number = value
                if self.prefix_normalization == "add_local" and self.local_country:
                    prefix = self.get_prefix_for_country(self.local_country)
                else:
                    prefix = None

            number = number.replace(" ", "")
            number, ext = self.split_extension(number)
            ext = ext.replace(";", "; ")
            ext = ext.replace(",", ", ")

            value = (
                ("+%d " % prefix if prefix is not None else "")
                + self.group_digits(number)
                + ext or ""
            )

        return value

    def _default_validation(self, context):

        for error in String._default_validation(self, context):
            yield error

        value = context.value

        if isinstance(value, basestring):

            valid = True

            # Remove the international prefix
            value = value.strip()
            if value.startswith("00"):
                value = value[2:].lstrip()

            # Obtain the country code
            if value.startswith("+"):
                try:
                    prefix, value = value.split(" ", 1)
                    prefix.lstrip("+")
                    prefix = int(prefix)
                except:
                    valid = False
                    prefix = None
                    country = None
                else:
                    country = self.get_country_from_prefix(prefix)
            else:
                prefix = None
                country = self.local_country

            if valid:
                # Possibly deny international numbers
                international_numbers = self.resolve_constraint(
                    self.international_numbers,
                    context
                )

                if prefix:
                    # - all international numbers
                    if international_numbers == "reject":
                        if country is None or country != self.local_country:
                            yield InternationalPhoneNumbersNotAllowedError(
                                context
                            )
                    # - just a subset
                    else:
                        accepted_countries = self.resolve_constraint(
                            self.accepted_countries,
                            context
                        )
                        if (
                            accepted_countries is not None
                            and (
                                country is None
                                or country not in accepted_countries
                            )
                        ):
                            yield InvalidPhoneCountryError(context)

                # Ignore extensions
                value = self.split_extension(value)[0]

                # Validate the country specific format
                value = value.replace(" ", "")

                if country:
                    format = self.get_country_format(country)
                else:
                    format = None

                if format:
                    valid = format.match(value)
                else:
                    number = value
                    if prefix is not None:
                        number = str(prefix) + number

                    valid = (
                        len(number) <= 15
                        and all((c in digits) for c in number)
                    )

            if not valid:
                yield PhoneFormatError(context)

    @classmethod
    def split_extension(cls, number):

        comma = number.find(",")
        semicolon = number.find(";")

        if semicolon != -1 and (comma == -1 or semicolon < comma):
            return number[:semicolon], number[semicolon:]
        elif comma != -1:
            return number[:comma], number[comma:]

        return number, ""

    @classmethod
    def group_digits(self, number):

        number = number.replace(" ", "")

        count = len(number)
        if count < 5:
            return number

        groups = []
        i = 0
        n = 3

        while i < count:
            groups.append(number[i:i + n])
            i += n
            if n == 3:
                r = (count - i)
                if r < 5 and r != 3:
                    n = 2

        return " ".join(groups)


PhoneNumber.set_country_info("ad", 376, re.compile(r"^\d{6}(\d{3})?$"))
PhoneNumber.set_country_info("es", 34, NINE_DIGITS_EXPR)
PhoneNumber.set_country_info("fr", 33, NINE_DIGITS_EXPR)
PhoneNumber.set_country_info("gi", 350, re.compile(r"^\d{8}$"))
PhoneNumber.set_country_info("pt", 351, NINE_DIGITS_EXPR)

