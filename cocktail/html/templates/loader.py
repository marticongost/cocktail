#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
import os
from pkg_resources import resource_filename
from cocktail.cache import Cache
from cocktail.pkgutils import import_object, set_full_name
from cocktail.html.templates.compiler import TemplateCompiler


class TemplateLoader(object):

    extension = ".cml"
    Compiler = TemplateCompiler

    class Cache(Cache):

        def _is_current(self, entry):
            template = entry.value
            return template.source_file \
                and entry.creation >= os.stat(template.source_file).st_mtime

    def __init__(self):
        self.__dependencies = {}
        self.__derivatives = {}

        self.cache = self.Cache()
        self.cache.expiration = None
        self.cache.load = self._load_template

    def get_class(self, name):
        """Obtains a python class from the specified template.
        
        @param name: The name of the template to obtain the class for.
        @type name: str

        @return: An instance of the requested template.
        @rtype: L{cocktail.html.Element}

        @raise TemplateNotFoundError: Raised if the indicated template can't be
            found on the loader's search path.
        """
        return self.cache.request(name)
    
    def new(self, name):
        """Produces an instance of the specified template.
        
        @param name: The name of the template to instantiate.
        @type name: str

        @return: An instance of the requested template.
        @rtype: L{cocktail.html.Element}
        
        @raise TemplateNotFoundError: Raised if the indicated template can't be
            found on the loader's search path.
        """
        return self.cache.request(name)()

    def compile(self, name, source):
        pkg_name, class_name = self._split_name(name)
        return self.Compiler(pkg_name, class_name, self, source)

    def _load_template(self, name):

        pkg_name, class_name = self._split_name(name)

        # Drop cached templates that depend on the requested template
        derivatives = self.__derivatives.get(name)

        if derivatives:
            for derivative in derivatives:
                self.cache.pop(derivative, None)
        
        # Discard previous dependencies
        dependencies = self.__dependencies.get(name)

        if dependencies:
            for dependency in dependencies:
                self.__derivatives[dependency].remove(name)

        # Try to obtain the template class from a template file
        try:
            source_file = self._find_template(pkg_name, class_name)
        except TemplateNotFoundError:
            source_file = None

        full_name = pkg_name + "." + class_name.lower() + "." + class_name

        if source_file is not None:

            try:
                f = file(source_file, "r")
                source = f.read()
            finally:
                f.close()

            compiler = self.Compiler(pkg_name, class_name, self, source)

            deps = compiler.classes.keys()
            self.__dependencies[name] = deps

            # Update the template dependency graph
            for dependency in deps:
                derivatives = self.__derivatives.get(dependency)

                if derivatives is None:
                    self.__derivatives[dependency] = derivatives = set()

                derivatives.add(name)
            
            cls = compiler.get_template_class()
            set_full_name(cls, full_name)

        # If no template file for the requested template is found, try to import
        # the template class from a regular python module
        # Note that by convention, foo.Bar becomes foo.bar.Bar
        else:
            try:
                cls = import_object(full_name)
            except ImportError:
                raise TemplateNotFoundError(name)

            self.__dependencies[name] = None

        cls.source_file = source_file
        return cls
   
    def _split_name(self, name):
        
        pos = name.rfind(".")

        if pos == -1:
            raise ValueError("Unqualified template name: " + name)

        pkg_name = name[:pos]
        item_name = name[pos + 1:]
        
        if not pkg_name or not item_name:
            raise ValueError("Wrong template name: %s" % name)
        
        return pkg_name, item_name

    def _find_template(self, pkg_name, class_name):
        """Finds the source file for a template, given its package and name.
        
        @param pkg_name: The full name of the package where the template
            resides.
        @type name: str

        @param name: The name of the template.
        @type name: str

        @return: The path to the file containing the source code for the
            specified template, None if no such file exists.
        @rtype: str

        @raise TemplateNotFoundError: Raised if the template package doesn't
            exist.
        """
        try:
            path = resource_filename(pkg_name, class_name + self.extension)
        except ImportError:
            path = None
        
        if path is None or not os.path.exists(path):
            raise TemplateNotFoundError(pkg_name + "." + class_name)
        
        return path


class TemplateNotFoundError(Exception):
    """An exception raised when a L{template loader<TemplateLoader>} can't find
    the requested template.

    @ivar name: The qualified name of the template that couldn't be found.
    @type name: str
    """

    def __init__(self, name):
        Exception.__init__(self, "Couldn't find template class '%s'" % name)
        self.name = name


if __name__ == "__main__":

    from sys import argv, exit

    if len(argv) != 2:
        print "Usage: %s <template file>" % argv[0]
        exit(1)

    loader = TemplateLoader()

    f = file(argv[1])
    source = f.read()
    f.close()

    class_source = TemplateCompiler(
        "_package_",
        "Template",
        loader,
        source
    ).get_source()

    for i, line in enumerate(class_source.split("\n")):
        print str(i + 1).rjust(5) + ": " + line

