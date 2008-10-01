#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
from cocktail.cache import Cache
from cocktail.html.templates.compiler import TemplateCompiler

class TemplateLoader(object):

    Compiler = TemplateCompiler

    def __init__(self):
        
        self.cache = Cache()
        self.cache.expiration = None
        self.cache.load = self.load_template
      
        self.ref_cache = Cache()
        self.ref_cache.expiration = None
        self.ref_cache.load = self.path_from_ref

    def get_class(self, ref = None, file = None):
        '''Obtains a python class from the specified template.
        
        @param ref: The qualified name of the template type to instantiate.
        @type ref: str

        @param file: The absolute path to the file containing the definition of
            the template type to instantiate.
        @type file: str

        @return: An instance of the requested template.
        @rtype: L{cocktail.html.Element}
        '''
        if ref is not None:
            file = self.ref_cache.request(ref)

        return self.cache.request(file)
                
    def new(self, ref = None, file = None):
        '''Produces an instance of the specified template.
        
        @param ref: The qualified name of the template type to instantiate.
        @type ref: str

        @param file: The absolute path to the file containing the definition of
            the template type to instantiate.
        @type file: str

        @return: An instance of the requested template.
        @rtype: L{cocktail.html.Element}
        '''
        return self.get_class(ref = ref, file = file)()

    def load_template(self, file):
        source = open(file).read()
        return self.Compiler(source).template_class
    
    def path_from_ref(self, ref):
        # TODO: Transform python references into template file paths
        pass

if __name__ == "__main__":
    from time import time
    
    loader = TemplateLoader()
    loader.cache.expiration = 1

    start = time()
    greeting = loader.new(file = "test.ckt")
    greeting.children[0].visible = True
    print time() - start

    greeting.add_class("big")
    print greeting.render()

