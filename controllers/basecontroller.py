#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cherrypy import expose
from cocktail.modeling import ListWrapper
from cocktail.html import templates


class BaseController(object):

    view_class = None

    def __init__(self):
        self.__handled_errors = []
        self.handled_errors = ListWrapper(self.__handled_errors)
        
    def add_handled_error(self, error_type):
        self.__handled_errors.append(error_type)

    @expose
    def index(self, *args, **kwargs):
        
        context = {}
                    
        try:
            self._init(context, *args, **kwargs)
            self._run(context)
        except Exception, error:            
            handled = any(
                isinstance(error, error_type)
                for error_type in self.__handled_errors
            )            
            if handled:
                context["error"] = error 
            else:
                raise

        view = self._create_view(context)
        self._init_view(view, context)
        return view.render_page()

    def _init(self, context):
        pass

    def _run(self, context):
        pass

    def _create_view(self, context):
        return templates.new(self.view_class)

    def _init_view(self, view, context):
        view.error = context.get("error")

