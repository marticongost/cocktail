#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
import os
import types
from unittest import TextTestRunner, defaultTestLoader
from cocktail.pkgutils import import_module

PY_EXTENSIONS = ".py", ".pyc", ".pyo"

runner_params = {
    "verbosity": 1
}

def main():
    
    from sys import argv
    paths = argv[1:]
    
    if paths:
        paths = ["cocktail.tests." + path for path in paths]
    else:
        paths = ["cocktail.tests"]
    
    test_names = set()
    
    def expand_path(path):

        try:
            obj = import_module(path)
        except ImportError, ex:
            raise
        else:
            if isinstance(obj, types.ModuleType) \
            and is_package_file(obj.__file__):

                pkg_path = os.path.dirname(obj.__file__)
                names = set()

                for name in os.listdir(pkg_path):
                    file_name, file_ext = os.path.splitext(name)

                    if os.path.isdir(os.path.join(pkg_path, name)):
                        expand_path(path + "." + file_name)
                    elif file_ext in PY_EXTENSIONS and file_name not in names:
                        names.add(file_name)
                        test_names.add(path + "." + file_name)

                return

        test_names.add(path)
        
    for path in paths:
        expand_path(path)

    test_suite = defaultTestLoader.loadTestsFromNames(test_names)
    TextTestRunner(**runner_params).run(test_suite)

def is_package_file(path):
    if os.path.isfile(path):
        file_name, file_ext = os.path.splitext(path)
        return os.path.split(file_name)[1] == "__init__" \
            and file_ext in PY_EXTENSIONS
    
    return False


if __name__ == "__main__":
    main()

