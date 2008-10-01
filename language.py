#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from threading import local

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


class NoActiveLanguageError(Exception):
    pass

