#-*- coding: utf-8 -*-
u"""Utilities covering typical HTML design patterns.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from itertools import izip, cycle

def alternate_classes(element, classes = ("odd", "even")):
    
    @element.when_ready
    def alternate_classes_handler():
        children = (child for child in element.children if child.rendered)
        for child, cls in izip(children, cycle(classes)):
            child.add_class(cls)
    
def first_last_classes(element, first_class = "first", last_class = "last"):

    @element.when_ready
    def first_last_classes_handler():
        for child in element.children:
            if child.rendered:
                child.add_class(first_class)
                break
        else:
            return

        for child in reversed(element.children):
            if child.rendered:
                child.add_class(last_class)

