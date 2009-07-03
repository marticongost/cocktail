#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from copy import copy
import cherrypy
from cocktail.modeling import ListWrapper, SetWrapper, getter, cached_getter
from cocktail.language import get_content_language
from cocktail import schema
from cocktail.persistence.query import Query
from cocktail.html.datadisplay import (
    NO_SELECTION,
    SINGLE_SELECTION,
    MULTIPLE_SELECTION
)
from cocktail.controllers.userfilter import get_content_type_filters
from cocktail.controllers.parameters import (
    get_parameter,
    FormSchemaReader,
    CookieParameterSource
)


class UserCollection(object):

    base_collection = None
    default_page_size = 15
    selection_mode = MULTIPLE_SELECTION
    available_languages = ()

    allow_type_selection = True
    allow_member_selection = True
    allow_language_selection = True
    allow_filters = True
    allow_sorting = True
    allow_paging = True

    def __init__(self, root_type):
        self._root_type = root_type
        self.__base_filters = []
        self.__parameter_sources = {}
    
    # Parameters
    #--------------------------------------------------------------------------
    @cached_getter
    def params(self):
        params = FormSchemaReader(strict = True)
        params.source = lambda k: self.get_parameter_source(k)(k)
        return params

    def get_parameter_source(self, param_name):
        source = self.__parameter_sources.get(param_name)
        return source if source is not None else cherrypy.request.params.get

    def set_parameter_source(self, param_name, source):
        self.__parameter_sources[param_name] = source

    # Type
    #--------------------------------------------------------------------------
    @getter
    def root_type(self):
        return self._root_type

    @cached_getter
    def type(self):
        type = self._root_type

        if self.allow_type_selection:
            type = self.params.read(
                schema.Reference("type", class_family = type, default = type)
            )

        return type

    @cached_getter
    def adapter(self):
        return None
    
    @cached_getter
    def schema(self):
        
        schema = self.type

        adapter = self.adapter
        if adapter is not None:
            schema = adapter.export_schema(schema)

        return schema

    # Members
    #--------------------------------------------------------------------------
    @cached_getter
    def members(self):

        members = self.default_members

        if self.allow_member_selection:
            members = self.params.read(
                schema.Collection("members",
                    type = set,
                    items = schema.String(enumeration = self.public_members),
                    default = members
                )
            )

        return members

    @cached_getter
    def default_members(self):
        return self.public_members

    @cached_getter
    def public_members(self):
        return set(self.schema.members().keys())

    def _get_member(self, key, translatable = False, from_type = False):
        
        if translatable:
            parts = key.split(".")
            name = parts[0]
        else:
            name = key

        try:
            schema = self.type if from_type else self.__schema
            member = schema[name]
        except KeyError:
            member = None
    
        if member is None or name not in self.public_members:
            return None

        if translatable and len(parts) > 1:
            member = member.translated_into(parts[1])

        return member
    
    # Languages
    #------------------------------------------------------------------------------
    @cached_getter
    def languages(self):
        
        languages = set([get_content_language()])

        if self.allow_language_selection:
            languages = self.params.read(
                schema.Collection("language",
                    type = set,
                    items = schema.String(enumeration = self.available_languages),
                    default = languages
                )
            )

        return languages

    # Filters
    #--------------------------------------------------------------------------
    @cached_getter
    def available_user_filters(self):
        return get_content_type_filters(self.type)

    @cached_getter
    def user_filters(self):
 
        user_filters = []

        if self.allow_filters:

            filter_source = self.get_parameter_source("filter")
            replacing_existing_filters = (
                "filter" in cherrypy.request.params
                and isinstance(filter_source, CookieParameterSource)
            )
                    
            filters_param = self.params.read(
                schema.Collection("filter", items = schema.String())
            )
            
            # Discard all persisted filter parameters (restoring filters
            # selectively isn't supported, it's all or nothing)
            if replacing_existing_filters:
                cookie_prefix = filter_source.get_cookie_name("filter_")
                for key in cherrypy.request.cookie.keys():
                    if key.startswith(cookie_prefix):
                        del cherrypy.request.cookie[key]
                        cherrypy.response.cookie[key] = ""
                        response_cookie = cherrypy.response.cookie[key]
                        response_cookie["max-age"] = 0
                        response_cookie["path"] = "/"

            if filters_param:
                
                available_filters = dict(
                    (filter.id, filter)
                    for filter in self.available_user_filters)

                for i, filter_id in enumerate(filters_param):
                    try:
                        filter_model = available_filters[filter_id]                    
                    except KeyError:
                        raise ValueError("Unknown filter: " + filter_id)
                    else:
                        filter = copy(filter_model)
                        filter.available_languages = self.available_languages
                        get_parameter(
                            filter.schema,
                            target = filter,
                            source = filter_source,
                            prefix = "filter_",
                            suffix = str(i)
                        )
                        user_filters.append(filter)

        return ListWrapper(user_filters)

    @cached_getter
    def base_filters(self):
        return ListWrapper(self.__base_filters)

    def add_base_filter(self, expression):    
        self.__base_filters.append(expression)
        self.discard_results()

    # Ordering
    #--------------------------------------------------------------------------   
    @cached_getter
    def order(self):

        order = []

        if self.allow_sorting:

            order_param = self.params.read(
                schema.Collection("order", items = schema.String())
            )

            if order_param:
                
                for key in order_param:

                    if key.startswith("-"):
                        sign = schema.expressions.NegativeExpression
                        key = key[1:]
                    else:
                        sign = schema.expressions.PositiveExpression

                    member = self._get_member(
                        key,
                        translatable = True,
                        from_type = True
                    )

                    if member:
                        order.append(sign(member))

        return ListWrapper(order)
    
    # Paging
    #--------------------------------------------------------------------------
    @cached_getter
    def page(self):
        page = None
        if self.allow_paging:
            return self.params.read(
                schema.Integer("page", min = 0, default = 0)
            )
        return page

    @cached_getter
    def page_size(self):
        page_size = None
        if self.allow_paging:
            return self.params.read(
                schema.Integer(
                    "page_size",
                    min = 0,
                    default = self.default_page_size
                )
            )
        return page_size

    # Selection
    #--------------------------------------------------------------------------
    @cached_getter
    def selection(self):

        if self.selection_mode == NO_SELECTION:
            return list()
        else:
            if self.selection_mode == SINGLE_SELECTION:
                param = schema.Reference("selection", type = self.type)
            else:
                param = schema.Collection(
                    "selection",
                    default = list(),
                    items = schema.Reference(type = self.type)
                )

            return self.params.read(param)

    # Results
    #--------------------------------------------------------------------------
    @cached_getter
    def subset(self):

        subset = Query(
            self.type,
            base_collection = self.base_collection
        )
        
        for expression in self.__base_filters:
            subset.add_filter(expression)

        for user_filter in self.user_filters:
            if user_filter.schema.validate(user_filter):
                subset.add_filter(user_filter.expression)

        for criteria in self.order:
            subset.add_order(criteria)

        return subset
    
    @cached_getter
    def page_subset(self):
        
        page_subset = self.subset
        page = self.page
        page_size = self.page_size

        if page_size:
            start = page * page_size
            end = start + page_size
            page_subset = page_subset[start:end]
    
        return page_subset

    def discard_results(self):
        self.__class__.subset.clear(self)
        self.__class__.page_subset.clear(self)

