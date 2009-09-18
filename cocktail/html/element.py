#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2007
"""
from inspect import getmro
from threading import local
from cocktail.modeling import getter, empty_list, empty_dict, empty_set
from cocktail.iteration import first
from cocktail.html.resources import Resource
from cocktail.html.overlay import apply_overlays

_thread_data = local()

default = object()

class Element(object):
    
    tag = "div"
    page_title = None
    styled_class = False
    scripted = True
    styled = True
    theme = None
    visible = True
    collapsible = False
    overlays_enabled = False
    generated_id_format = "cocktail-element%d"
    client_model = None

    # Data binding
    data_display = None
    data = None
    member = None
    language = None
    
    def __init__(self,
        tag = default,
        class_name = None,
        children = None,
        **attributes):
 
        self.__parent = None
        self.__children = None

        if children:
            for child in children:
                self.append(child)
        
        if attributes:
            self.__attributes = dict(attributes)
        else:
            self.__attributes = None
    
        if self.class_css:
            self["class"] = self.class_css

        if class_name:
            self.add_class(class_name)

        self.__meta = None
        self.__head_elements = None
        self.__resources = None
        self.__resource_uris = None
        self.__client_params = None
        self.__client_code = None
        self.__client_variables = None
        self.__client_translations = None
        self.__is_ready = False
        self.__binding_handlers = None
        self.__ready_handlers = None

        if tag is not default:
            self.tag = tag
         
        if self.overlays_enabled:
            apply_overlays(self)

        self._build()

    class __metaclass__(type):

        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
         
            if "overlays_enabled" not in members:
                cls.overlays_enabled = True

            # Aggregate CSS classes from base types
            cls._classes = list(getmro(cls))[:-1]
            cls._classes.reverse()
            css_classes = []

            if "styled_class" not in members:
                cls.styled_class = True

            for c in cls._classes:
                if getattr(c, "styled_class", False):                
                    css_classes.append(c.__name__)

            cls.class_css = css_classes and " ".join(css_classes) or None

    def __str__(self):

        if self.tag is None:
            return "html block"
        else:
            desc = "<" + self.tag
            
            id = self["id"]

            if id:
                desc += " id='%s'" % id

            css = self["class"]

            if css:
                desc += " class='%s'" % css

            desc += ">"
            return desc

    # Rendering
    #--------------------------------------------------------------------------

    def make_page(self, renderer = None):
 
        if not renderer:
            renderer = self._get_default_renderer()

        return renderer.make_page(self)

    def render_page(self, renderer = None):
        
        if not renderer:
            renderer = self._get_default_renderer()
        
        return self.make_page(renderer).render(renderer)

    def render(self, renderer = None):

        if not renderer:
            renderer = self._get_default_renderer()
        
        canvas = []
        out = canvas.append
        
        if not hasattr(_thread_data, "generated_id"):
            _thread_data.generated_id = 0
            try:
                self._render(renderer, out)
            finally:
                del _thread_data.generated_id
        else:
            self._render(renderer, out)
        
        return u"".join(canvas)

    def _get_default_renderer(self):
        from cocktail.html.renderers import DEFAULT_RENDERER_TYPE
        return DEFAULT_RENDERER_TYPE()

    def _render(self, renderer, out):
        self.ready()
        if self.rendered:
            renderer.write_element(self, out)

    def _build(self):
        pass

    def ready(self):

        if not self.__is_ready:

            # Binding            
            self._binding()

            if self.__binding_handlers:
                for handler in self.__binding_handlers:
                    handler()
            
            # Ready
            self._ready()
            
            if self.__ready_handlers:
                for handler in self.__ready_handlers:
                    handler()

            if self.__client_params or self.__client_code:
                self.require_id()

            if self.member: 
                self.add_class(self.member.__class__.__name__)

            self.__is_ready = True
    
    def when_binding(self, handler):
        if self.__binding_handlers is None:
            self.__binding_handlers = [handler]
        else:
            self.__binding_handlers.append(handler)

    def when_ready(self, handler):
        if self.__ready_handlers is None:
            self.__ready_handlers = [handler]
        else:
            self.__ready_handlers.append(handler)

    def _binding(self):
        pass

    def _ready(self):
        pass

    def _content_ready(self):
        pass

    def _descendant_ready(self, descendant):
        pass

    # Attributes
    #--------------------------------------------------------------------------
    
    @getter
    def attributes(self):
        if self.__attributes is None:
            return empty_dict
        else:
            return self.__attributes

    def __getitem__(self, key):
        if self.__attributes is None:
            return None
        else:
            return self.__attributes.get(key)

    def __setitem__(self, key, value):
        if self.__attributes is None:
            if value is not None:
                self.__attributes = {key: value}
        else:
            if value is None:
                self.__attributes.pop(key, None)
            else:
                self.__attributes[key] = value

    def __delitem__(self, key):
        if self.__attributes is not None:
            self.__attributes.pop(key, None)

    def require_id(self):

        id = self["id"]

        if not id:
            try:
                incremental_id = _thread_data.generated_id
            except AttributeError:
                raise IdGenerationError()

            _thread_data.generated_id += 1

            id = self.generated_id_format % incremental_id
            self["id"] = id

        return id

    # Visibility
    #--------------------------------------------------------------------------
    
    @getter
    def rendered(self):
        return self.visible \
            and (not self.collapsible or self.has_rendered_children())
        
    @getter
    def substantial(self):
        return self.rendered

    def has_rendered_children(self):

        if self.__children:
            for child in self.__children:
                if child.substantial:                
                    return True

        return False

    # Tree
    #--------------------------------------------------------------------------

    @getter
    def parent(self):
        return self.__parent

    @getter
    def children(self):
        if self.__children is None:
            return empty_list
        else:
            return self.__children
    
    def append(self, child):
     
        if isinstance(child, basestring):
            child = Content(child)
        else:
            child.release()

        if self.__children is None:
            self.__children = [child]
        else:
            self.__children.append(child)
        
        child.__parent = self

    def insert(self, index, child):
        
        if isinstance(child, basestring):
            child = Content(child)
        else:
            child.release()

        if self.__children is None:
            self.__children = []

        self.__children.insert(index, child)
        child.__parent = self

    def place_before(self, sibling):
        
        if sibling.__parent is None:
            raise ElementTreeError()

        self.release()

        sibling.__parent.__children.insert(
            sibling.__parent.__children.index(sibling),
            self
        )

        self.__parent = sibling.__parent

    def place_after(self, sibling):
        
        if sibling.__parent is None:
            raise ElementTreeError()

        self.release()

        sibling.__parent.__children.insert(
            sibling.__parent.__children.index(sibling) + 1,
            self
        )

        self.__parent = sibling.__parent

    def empty(self):

        if self.__children is not None:
            for child in self.__children:
                child.__parent = None

            self.__children = None

    def release(self):
        
        if self.__parent is not None:
            self.__parent.__children.remove(self)
            self.__parent = None

    def reverse(self):
        if self.__children:
            self.__children.reverse()

    # CSS classes
    #--------------------------------------------------------------------------

    @getter
    def classes(self):
        
        css_class = self["class"]

        if css_class is None:
            return empty_list
        else:
            return css_class.split()

    def add_class(self, name):
        
        css_class = self["class"]

        if css_class is None:
            self["class"] = name
        else:
            if name not in css_class.split():
                self["class"] = css_class + " " + name

    def remove_class(self, name):
        
        css_class = self["class"]
        
        if css_class is not None:
            classes = css_class.split()
            try:
                css_class = classes.remove(name)
            except ValueError:
                pass
            else:
                if classes:
                    self["class"] = " ".join(classes)
                else:
                    del self["class"]

    # Inline CSS styles
    #--------------------------------------------------------------------------
    
    @getter
    def style(self):
        
        style = self["style"]

        if style is None:
            return empty_dict
        else:
            style_dict = {}

            for declaration in style.split(";"):
                prop, value = declaration.split(":")
                style_dict[prop.strip()] = value.strip()

            return style_dict

    def get_style(self, property):
        return self.style.get(property)

    def set_style(self, property, value):
        style = self.style

        if style:
            if value is None:
                style.pop(property, None)
            else:
                style[property] = value

            if style:
                self["style"] = \
                    "; ".join("%s: %s" % decl for decl in style.iteritems())
            else:
                del self["style"]
        else:
            self["style"] = "%s: %s" % (property, value)

    # Resources
    #--------------------------------------------------------------------------
    
    @getter
    def resources(self):
        if self.__resources is None:
            return empty_list
        else:
            return self.__resources

    @getter
    def resource_uris(self):
        if self.__resource_uris is None:
            return empty_set
        else:
            return self.__resource_uris

    def add_resource(self, resource):
        
        # Normalize the resource
        if isinstance(resource, basestring):
            uri = resource
            resource = Resource.from_uri(uri)
        else:
            uri = resource.uri
            
            if uri is None:
                raise ValueError("Can't add a resource without a defined URI.")

        if self.__resources is None:
            self.__resources = [resource]
            self.__resource_uris = set([uri])
            return True
        elif uri not in self.__resource_uris:
            self.__resources.append(resource)
            self.__resource_uris.add(resource.uri)
            return True
        else:
            return False

    def remove_resource(self, resource):

        if isinstance(resource, basestring):
            removed_uri = resource
            resource = first(self.__resources, uri = removed_uri)

            if resource is None:
                raise ValueError("Error removing '%s' from %s: "
                    "the element doesn't have a resource with that URI")
            else:
                self.__resources.remove(resource)
                self.__resource_uris.remove(removed_uri)
        else:
            self.__resources.remove(resource)
            self.__resource_uris.remove(resource.uri)

    # Meta attributes
    #--------------------------------------------------------------------------
    
    @getter
    def meta(self):
        if self.__meta is None:
            return empty_dict
        else:
            return self.__meta

    def get_meta(self, key):
        if self.__meta is None:
            return None
        else:
            return self.__meta.get(key)

    def set_meta(self, key, value):
        if self.__meta is None:
            if value is not None:
                self.__meta = {key: value}
        else:
            if value is None:
                self.__meta.pop(key, None)
            else:
                self.__meta[key] = value

    # Head elements
    #--------------------------------------------------------------------------
    
    @getter
    def head_elements(self):
        if self.__head_elements is None:
            return empty_list
        else:
            return self.__head_elements

    def add_head_element(self, element):
        if self.__head_elements is None:
            self.__head_elements = [element]
        else:
            self.__head_elements.append(element)

    # Client side element parameters
    #--------------------------------------------------------------------------
    
    @getter
    def client_params(self):
        if self.__client_params is None:
            return empty_dict
        else:
            return self.__client_params
    
    def get_client_param(self, key):
        if self.__client_params is None:
            raise KeyError("Trying to read an undefined "
                "client param '%s' on %s" % (key, self))
        else:
            return self.__client_params[key]

    def set_client_param(self, key, value):
        if self.__client_params is None:
            self.__client_params = {key: value}
        else:
            self.__client_params[key] = value

    def remove_client_param(self, key):
        if self.__client_params is None:
            raise KeyError("Trying to remove an undefined "
                "client param '%s' on %s" % (key, self))
        else:
            del self.__client_params[key]
    
    # Client side element initialization code
    #--------------------------------------------------------------------------
    
    @getter
    def client_code(self):
        if self.__client_code is None:
            return empty_list
        else:
            return self.__client_code
    
    def add_client_code(self, snippet):
        if self.__client_code is None:
            self.__client_code = [snippet]
        else:
            self.__client_code.append(snippet)

    # Client side variables
    #--------------------------------------------------------------------------

    @getter
    def client_variables(self):
        if self.__client_variables is None:
            return empty_dict
        else:
            return self.__client_variables
    
    def get_client_variable(self, key):
        if self.__client_variables is None:
            raise KeyError("Trying to read an undefined "
                "client variable '%s' on %s" % (key, self))
        else:
            return self.__client_variables[key]

    def set_client_variable(self, key, value):
        if self.__client_variables is None:
            self.__client_variables = {key: value}
        else:
            self.__client_variables[key] = value

    def remove_client_variable(self, key):
        if self.__client_variables is None:
            raise KeyError("Trying to remove an undefined "
                "client variable '%s' on %s" % (key, self))
        else:
            del self.__client_variables[key]

    # Client side translations
    #--------------------------------------------------------------------------
    
    @getter
    def client_translations(self):
        if self.__client_translations is None:
            return empty_set
        else:
            return self.__client_translations
    
    def add_client_translation(self, key):
        if self.__client_translations is None:
            self.__client_translations = set()
        self.__client_translations.add(key)
        

class Content(Element):
 
    styled_class = False
    value = None
    overlays_enabled = False

    def __init__(self, value = None, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self.value = value
 
    @getter
    def rendered(self):
        return self.visible
    
    @getter
    def substantial(self):
        return self.visible and unicode(self.value).strip()

    def _render(self, render, out):
        self.ready()
        if self.value is not None:
            out(unicode(self.value))


class PlaceHolder(Content):

    def __init__(self, expression):
        Content.__init__(self)
        self.expression = expression

    def _ready(self):
        self.value = self.expression()


class ElementTreeError(Exception):
    pass


class IdGenerationError(Exception):

    def __str__(self):
        return "Element identifiers can only be generated "\
               "during page rendering"

