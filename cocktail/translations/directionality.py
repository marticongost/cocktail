#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from threading import local

_thread_data = local()

defaults = {
    "*": "ltr",
    "ar": "rtl",
    "he": "rtl"
}

def get(locale):
    mapping = getattr(_thread_data, "directionality", None)
    direction = None if mapping is None else mapping.get(locale)
    if direction is None:
        direction = defaults.get(locale)
    return direction or get("*")

def set(locale, direction):
    mapping = getattr(_thread_data, "directionality", None)
    if mapping is None:
        mapping = {}
        _thread_data.directionality = mapping
    mapping[locale] = direction

