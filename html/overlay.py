#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from inspect import getmro
from types import FunctionType
from cocktail.modeling import empty_list, extend, call_base

_overlays = {}

def apply_overlays(element):
    """Initialize an element with the modifications provided by all matching
    overlays. Overlays are applied in the same order they were registered in.

    @param element: The element to apply the overlays to.
    @type element: L{Element<cocktail.html.element.Element>}
    """
    for cls in element.__class__._classes:
        class_overlays = _overlays.get(cls)
        if class_overlays:
            for overlay in class_overlays:
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
    excluded_keys = set(["__module__", "_classes", "__doc__"])

    class __metaclass__(type):
        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            cls._classes = [c
                            for c in reversed(getmro(cls))
                            if Overlay
                            and c is not Overlay
                            and issubclass(c, Overlay)]

    @classmethod
    def register(cls, target):
        """Installs the overlay on the indicated class. All new instances of
        the modified class will reflect the changes introduced by the overlay
        (existing instances will remain unchanged).

        @param target: The class to install the overlay on.
        @type target: Class or str
        """
        from cocktail.html import templates

        if isinstance(target, basestring):
            target = templates.get_class(target)
        
        class_overlays = _overlays.get(target)

        if not class_overlays:
            class_overlays = []
            _overlays[target] = class_overlays
        
        class_overlays.append(cls)
       
    @classmethod
    def modify(cls, element):

        for key, value in cls.__dict__.iteritems():
            
            if key in cls.excluded_keys:
                continue

            if isinstance(value, FunctionType):
                extend(element)(value)
            else:
                setattr(element, key, value)

