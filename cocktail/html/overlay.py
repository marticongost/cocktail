#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from inspect import getmro
from types import FunctionType
from cocktail.modeling import (
    classgetter,
    extend, 
    call_base, 
    OrderedSet
)
from cocktail.pkgutils import get_full_name

_overlays = {}


def register_overlay(class_name, overlay_name):
    """Installs an overlay on the indicated class. All new instances of
    the modified class will reflect the changes introduced by the overlay
    (existing instances will remain unchanged).

    :param class_name: The name of the class to install the overlay on.
    :type class_name: str

    :param overlay_name: The name of the class that implements the overlay.
    :type overlay_name: str
    """
    class_overlays = _overlays.get(class_name)

    if not class_overlays:
        _overlays[class_name] = class_overlays = OrderedSet()
 
    class_overlays.append(overlay_name)

def get_class_overlays(cls):
    """Determine the overlayed classes that apply to the specified class.

    :param cls: The class to determine the overlays for.
    :type cls: `Element` class
    
    :return: An iterable sequence of overlay classes that apply to the
        specified class.
    :rtype: Iterable sequence of `Overlay` classes
    """
    if _overlays:
        for cls in reversed(cls.__mro__):
            view_name = getattr(cls, "view_name", None)
            if view_name:
                class_overlays = _overlays.get(view_name)
                if class_overlays:
                    from cocktail.html import templates
                    for overlay_name in class_overlays:
                        yield templates.get_class(overlay_name)

def apply_overlays(element):
    """Initialize an element with the modifications provided by all matching
    overlays. Overlays are applied in the same order they were registered in.

    @param element: The element to apply the overlays to.
    @type element: L{Element<cocktail.html.element.Element>}
    """
    for overlay in get_class_overlays(element.__class__):
        overlay.modify(element)


# Declaration stub, required by the metaclass
Overlay = None


class Overlay(object):
    """Base (abstract) class for all overlays. An overlay represents a set of
    modifications to an L{Element<cocktail.html.element.Element>} class.
    Overlays can extend an existing class with new content and/or alter its
    existing elements, in a clean, reusable and unobtrusive way.
    
    To create an overlay, subclass this base class or another overlay class,
    and invoke the L{register} method on the new class. All methods and
    attributes defined by the overlay will be made available to its target.
    """
    excluded_keys = set(["__module__", "__doc__"])

    @classmethod
    def modify(cls, element):

        for key, value in cls.__dict__.iteritems():
            
            if key in cls.excluded_keys:
                continue

            if isinstance(value, FunctionType):
                extend(element)(value)
            else:
                setattr(element, key, value)

    _view_name = None

    @classgetter
    def view_name(cls):
        if cls._view_name is None:
            cls._view_name = get_view_full_name(get_full_name(cls))
        return cls._view_name

