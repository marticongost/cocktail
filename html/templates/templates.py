#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
from time import time
from os import stat

def load_template(**kwargs):
    return load_template_class(**kwargs)()

def load_template_class(source = None, path = None, module = None):

    if (source is not None) + (path is not None) + (module is not None) > 1:
        raise ValueError("Error loading a template: parameters `source`, "
                "`path` and `module` are mutually exclusive")
    
    if module:
        path = ...

    if path:
        f = open(path, "r")
        source = f.read()
        f.close()
    
    return path, source

class TemplateManager(object):
    
    capacity = None
    expiration = None
    reload_outdated = True

    def __init__(self):
        self.__cached_entries = {}
        
    def get_template(self, **kwargs):
        pass

    def get_template_class(self, **kwargs):
        pass

    def drop_template_class(self, **kwargs):
        pass

    def _drop_excess(self):
        pass

    class CachedTemplate(object):
        mtime = None
        path = None
        template_class = None

