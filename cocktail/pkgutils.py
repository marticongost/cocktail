#-*- coding: utf-8 -*-
"""
Provides importing and naming services for packages, modules and their exported
objects.
"""
import sys
import os.path
import pkgutil
from types import ModuleType

PYTHON_EXTENSIONS = ".py", ".pyc", ".pyo", ".pyd"

def resource_filename(module_name, *args):
    """Retrieves a path relative to the given module.

    This is analogous to `pkg_resources.resource_filename`, but it doesn't
    import the module.

    :param module_name: The name of the module that contains the requested
        resource.
    :type module_name: str

    :param args: Any number of additional arguments; will be appended to the
        produced path.
    :type args: str

    :return: The path of the indicated resource.
    :rtype: str

    :raise ImportError: Raised if the indicated module can't be found.
    """
    module = pkgutil.get_loader(module_name)
    if module is None:
        raise ImportError("Can't find module %s" % module_name)
    return os.path.join(os.path.dirname(module.path), *args)

def resolve(reference):
    """Resolves a reference to an object.

    The refered object can be specified using a fully qualified name, which
    will be imported, or an object reference, which will be returned as is.

    :param name: The reference to resolve.
    :type name: str or object

    :return: The refered object.
    :rtype: object

    :raise: Raises `ImportError` if there's no module or package matching the
        indicated qualified name.

    :raise: Raises `AttributeError` if the indicated module or package doesn't
        contain the requested object.
    """
    if isinstance(reference, str):
        return import_object(reference)
    else:
        return reference

def import_module(name):
    """Obtains a reference to a module or package from a qualified name.

    :param name: The fully qualified name of the module to import.
    :type name: str

    :return: The requested module.
    :rtype: object

    :raise: Raises `ImportError` if there's no module or package matching the
        indicated qualified name.
    """
    obj = __import__(name)

    for component in name.split(".")[1:]:
        obj = getattr(obj, component)

    return obj

def import_object(name):
    """Obtains a reference to an object from a qualified name.

    :param name: The fully qualified name of the object to import.
    :type name: str

    :return: The requested object.
    :rtype: object

    :raise: Raises `ImportError` if there's no module or package matching the
        indicated qualified name.

    :raise: Raises `AttributeError` if the indicated module or package doesn't
        contain the requested object.
    """
    components = name.split(".")
    obj = __import__(".".join(components[:-1]))

    for component in components[1:]:
        try:
            obj = getattr(obj, component)
        except AttributeError:
            raise ImportError("Can't import name %s" % name)

    return obj

_full_names = {}

def get_full_name(obj):
    """Obtains the canonical qualified name for the provided object.

    :param obj: The object to determine the name for.
    :type obj: Package, module, class, function or method

    :return: The qualified name of the object.
    :rtype: str

    :raise: Raises `TypeError` if the provided object is an instance of a type
        that can't map its instances to qualified names.
    """
    name = _full_names.get(obj)

    if name is None:

        if isinstance(obj, ModuleType):

            if obj.__name__ == "__main__":
                name = get_path_name(sys.argv[0])
            else:
                return obj.__name__
        else:
            module_name = getattr(obj, "__module__", None)

            if module_name == "__builtin__":
                prefix = ""
            else:
                prefix = get_full_name(sys.modules[module_name]) + "."

            if module_name:

                # Classes
                if isinstance(obj, type):
                    name = prefix + obj.__name__
                else:
                    # Methods
                    func = getattr(obj, "__func__", None)
                    self = getattr(obj, "__self__", None)

                    if func and self:
                        name = "%s%s.%s" \
                            % (prefix, self.__class__.__name__, func.__name__)
                    else:
                        # Functions
                        func_name = getattr(obj, "__name__", None)

                        if func_name:
                            name = prefix + func_name

        # Store the name for future requests
        if name:
            _full_names[obj] = name

    if name is not None:
        return name
    else:
        raise TypeError("Can't find the name of %r" % obj)

def set_full_name(obj, name):
    """Sets the canonical, fully qualified name of the provided python object.

    This function will override the normal behavior of `get_full_name` on the
    given object, so that it always returns the assigned name. This can be used
    to supply qualified names for objects that can't be normally mapped to a
    name (for example, templates produced by `cocktail.html.templates`).

    :param obj: The object to establish the name for.
    :type obj: Package, module, class, function or method

    :param name: The qualified name to assign to the object.
    :type name: str
    """
    _full_names[obj] = name

def get_path_name(path):
    """Gets the qualified name of the module or package that maps to the
    indicated file or folder.

    :param path: The path to the file or folder to evaluate.
    :type path: str

    :return: The fully qualified name of the package or module at the indicated
        location.

    :raise: Raises `ValueError` if the indicated path doesn't map to a python
        module or package.
    """
    components = []

    # Normalize the path
    path = os.path.abspath(path)

    if path[-1] == os.path.sep:
        path = path[:-1]

    # Descend the filesystem hierarchy
    while path:

        parent_path, path_component = os.path.split(path)

        # Modules
        if os.path.isfile(path):

            fname, ext = os.path.splitext(path_component)

            if ext not in PYTHON_EXTENSIONS:
                raise ValueError(
                    "%r doesn't map to a python module or package"
                    % path
                )

            if fname != "__init__":
                components.append(fname)

        # Packages
        elif os.path.isdir(path):

            if any(
                os.path.isfile(os.path.join(path, "__init__" + ext))
                for ext in PYTHON_EXTENSIONS
            ):
                components.append(path_component)
            else:
                break
        else:
            raise ValueError(
                "Error resolving the python name for path %r: "
                "wrong path"
                % path
            )

        path = parent_path

    return ".".join(reversed(components))

