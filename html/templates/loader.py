#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
import os
from cocktail.cache import Cache
from cocktail.html.templates.compiler import TemplateCompiler

class TemplateLoader(object):

    Compiler = TemplateCompiler

    class Cache(Cache):

        def _is_current(self, entry):
            return entry.creation >= os.stat(entry.key).st_mtime

    def __init__(self):
        
        self.paths = []

        self.cache = self.Cache()
        self.cache.expiration = None
        self.cache.load = self.compile_file

    def get_class(self, name):
        """Obtains a python class from the specified template.
        
        @param name: The name of the template to obtain the class for.
        @type name: str

        @return: An instance of the requested template.
        @rtype: L{cocktail.html.Element}

        @raise IOError: Raised if the indicated template can't be found on the
            loader's search path.
        """
        template_file = self._find_template(name)
        return self.cache.request(template_file)
                
    def new(self, name):
        """Produces an instance of the specified template.
        
        @param name: The name of the template to instantiate.
        @type name: str

        @return: An instance of the requested template.
        @rtype: L{cocktail.html.Element}
        
        @raise IOError: Raised if the indicated template can't be found on the
            loader's search path.
        """
        return self.get_class(name)()

    def _find_template(self, name):
        """Finds the source file for a template, given its name."""
        for path in self.paths:
            fname = os.path.join(path, name)
            if os.path.exists(fname):
                return fname

        raise IOError("Can't find template " + name)

    def compile_file(self, template_file):
        
        try:
            f = file(template_file, "r")
            source = f.read()
        finally:
            f.close()
        
        name = os.path.splitext(os.path.split(template_file)[1])[0]
        return self.Compiler(source, name).template_class
   

if __name__ == "__main__":

    loader = TemplateLoader()
    loader.paths.append("/home/marti/Projectes/sitebasis/src/sitebasis/views")
    
    from time import time

    for i in range(2):
        t = time()
        loader.get_class("Installer.xml")
        print time() - t

