#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from cocktail.html import templates, renderers


class CocktailBuffetPlugin(object):

    def __init__(self, extra_vars_func=None, options=None):
        """The standard constructor takes an 'extra_vars_func',
        which is a callable that is called for additional
        variables with each rendering. Options is a dictionary
        that provides options specific to template engines
        (encoding, for example). The options should be
        prefixed with the engine's scheme name to allow the
        same dictionary to be passed in to multiple engines
        without ill effects."""
        self.extra_vars_func = extra_vars_func
        self._options = options

    def load_template(self, templatename, template_string = None):
        """Find a template specified in python 'dot' notation, or load one from
        a string."""
        if template_string is not None:
            loader = templates.get_loader()
            return loader.compile(templatename, template_string)
        else:
            return templates.get_class(templatename)

    # info is the dictionary returned by the user's controller.
    # format may only make sense for template engines that can
    # produce different styles of output based on the same
    # template.
    # fragment is used if there are special rules about rendering
    # a part of a page (don't include headers and declarations).
    # template is the name of the template to render.
    # You should incorporate extra_vars_func() output
    # into the namespace in your template if at all possible.
    def render(self, info, format="html", fragment=False, template=None):
        "Renders the template to a string using the provided info."

        if isinstance(template, basestring):
            element = templates.new(template)
        else:
            element = template()

        if self.extra_vars_func:
            for key, value in self.extra_vars_func().iteritems():
                setattr(element, key, value)

        for key, value in info.iteritems():
            setattr(element, key, value)

        renderer = None

        if format == "html":
            renderer = renderers.HTML4Renderer()
        elif format == "xhtml":
            renderer = renderers.XHTMLRenderer()
        elif format:
            raise ValueError("Can't render '%s' using format '%s'"
                % (template, format))

        if fragment:
            return element.render()
        else:
            return element.render_page()

    # This method is not required for most uses of templates.
    # It is specifically used for efficiently inserting widget
    # output into Kid pages. It does the same thing render does,
    # except the output is a generator of ElementTree Elements
    # rather than a string.
    def transform(self, info, template):
        "Render the output to Elements"
        pass

