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

    def __init__(self, *args, **kwargs):
        String.__init__(self, *args, **kwargs)
        self.add_validation(PhoneNumber.phone_number_validation)

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
                    pass
                else:
                    value = number.replace(" ", "")
                    if (
                        self.prefix_normalization != "strip_local"
                        or not self.local_country
                        or self.get_country_from_prefix(int(prefix))
                           != self.local_country
                    ):
                        value = "+" + str(prefix) + " " + value
            else:
                value = value.replace(" ", "")
                if self.prefix_normalization == "add_local" and self.local_country:
                    value = "+%d %s" % (
                        self.get_prefix_for_country(self.local_country),
                        value
                    )

        return value

    def phone_number_validation(self, value, context):

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
                                self,
                                value,
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
                            yield InvalidPhoneCountryError(
                                self,
                                value,
                                context
                            )

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
                yield PhoneFormatError(self, value, context)


PhoneNumber.set_country_info("ad", 376, re.compile(r"^\d{6}(\d{3})?$"))
PhoneNumber.set_country_info("es", 34, NINE_DIGITS_EXPR)
PhoneNumber.set_country_info("fr", 33, NINE_DIGITS_EXPR)
PhoneNumber.set_country_info("gi", 350, re.compile(r"^\d{8}$"))
PhoneNumber.set_country_info("pt", 351, NINE_DIGITS_EXPR)

