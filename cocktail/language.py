#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from threading import local
from contextlib import contextmanager

_thread_data = local()

def get_content_language():
    return getattr(_thread_data, "language", None)

def set_content_language(language):
    _thread_data.language = language

def require_content_language(language = None):
    
    if language is None:
        language = get_content_language()

    if language is None:
        raise NoActiveLanguageError()

    return language

@contextmanager
def content_language_context(language):

    prev_language = get_content_language()

    try:
        set_content_language(language)
        yield prev_language
    finally:
        set_content_language(prev_language)


class NoActiveLanguageError(Exception):
    """Raised when trying to access a translated member without defining the "
    "active content language first.
    """

