#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
import os
from pkg_resources import resource_filename
from cocktail.modeling import extend
from cocktail.cache import Cache
from cocktail.pkgutils import import_object, set_full_name
from cocktail.html.templates.compiler import TemplateCompiler


class TemplateLoaderCache(Cache):

    checks_modification_time = True
    expiration = None

    def _is_current(self, entry):
        
        if not Cache._is_current(self, entry):
            return False

        # Reload templates if their source file has been modified since
        # they were loaded
        if self.checks_modification_time:
            template = entry.value
            if template.source_file \
            and entry.creation < os.stat(template.source_file).st_mtime:
                return False
 
        # Reload templates if their dependencies need to be reloaded
        return all(
            self._is_current(self[dependency])
            for dependency in self._loader.iter_dependencies(entry.key)
        )


class TemplateLoader(object):
    """A class that loads template classes from their source files.

    @var cache: The cache used by the loader to store requested templates.
    @type: L{Cache<cocktail.cache.Cache>}
    """
    extension = ".cml"
    Compiler = TemplateCompiler
    Cache = TemplateLoaderCache
    
    def __init__(self):
        self.__dependencies = {}
        self.__derivatives = {}

        self.cache = self.Cache(self._load_template)
        self.cache._loader = self

        @extend(self.cache)
        def _entry_removed(cache, entry):
            self._forget_template(entry.key)

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

    def iter_dependencies(self, name, recursive = True, include_self = False):
        if include_self:
            yield name

        dependencies = self.__dependencies.get(name)

        if dependencies:
            if recursive:
                for dependency in dependencies:
                    for recursive_dependency \
                    in self.iter_dependencies(dependency, include_self = True):
                        yield recursive_dependency
            else:
                for dependency in dependencies:
                    yield dependency

    def _load_template(self, name):

        pkg_name, class_name = self._split_name(name)

        # Try to obtain the template class from a template file
        try:
            source_file = self._find_template(pkg_name, class_name)
        except TemplateNotFoundError:
            source_file = None

        full_name = pkg_name + "." + class_name.lower() + "." + class_name

        if source_file is not None:

            # Read the template's source
            f = file(source_file, "r")
            try:
                source = f.read()
            finally:
                f.close()

            # Compile the template's source
            compiler = self.Compiler(pkg_name, class_name, self, source)

            # Update the template dependency graph
            dependencies = set()
            self.__dependencies[name] = dependencies
            
            for dependency in compiler.classes.keys():

                dependencies.add(dependency)
                dependency_derivatives = self.__derivatives.get(dependency)

                if dependency_derivatives is None:
                    dependency_derivatives = set()
                    self.__derivatives[dependency] = dependency_derivatives

                dependency_derivatives.add(name)

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
   
    def _forget_template(self, name):

        # Clear the dependency declarations for the previous version of the
        # template
        dependencies = self.__dependencies.get(name)

        if dependencies:
            for dependency in dependencies:
                self.__derivatives[dependency].remove(name)

            del self.__dependencies[name]

        # Drop cached templates that depend on the requested template,
        # recursively
        derivatives = self.__derivatives.get(name)

        if derivatives:
            for derivative in list(derivatives):
                self.cache.pop(derivative, None)
            
            del self.__derivatives[name]

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

