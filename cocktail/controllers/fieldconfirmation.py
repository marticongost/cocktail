#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.events import when
from cocktail.schema.exceptions import ValidationError

translations.load_bundle("cocktail.controllers.fieldconfirmation")


def field_confirmation(member_name):
    """A decorator that adds a confirmation field for the given member of a
    form.
    """

    def decorator(form_class):

        @when(form_class.declared)
        def modify_form(e):

            form = e.source
            source_member = form.schema.get_member(member_name)
            confirmation_member_name = member_name + "_confirmation"
            confirmation_member = source_member.copy(
                name = confirmation_member_name,
                custom_translation_key =
                    "cocktail.controllers.fieldconfirmation."
                    "confirmation_field",
                after_member = member_name
            )

            form.adapter.exclude(confirmation_member_name)

            @confirmation_member.add_validation
            def validate_confirmation(ctx):
                source = ctx.get_value(member_name)
                confirmation = ctx.get_value(confirmation_member_name)
                if source and confirmation and source != confirmation:
                    yield ConfirmationError(ctx)

            form.schema.add_member(confirmation_member)
            return form

        return form_class

    return decorator


class ConfirmationError(ValidationError):
    pass

