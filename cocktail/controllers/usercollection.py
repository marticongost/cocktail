#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from copy import copy
import cherrypy
from cocktail.pkgutils import resolve
from cocktail.modeling import ListWrapper, SetWrapper, getter, cached_getter
from cocktail.translations import get_language
from cocktail import schema
from cocktail.schema.io import export_file
from cocktail.schema.expressions import (
    PositiveExpression,
    NegativeExpression,
    TranslationExpression
)
from cocktail.persistence.query import Query
from cocktail.html.datadisplay import (
    NO_SELECTION,
    SINGLE_SELECTION,
    MULTIPLE_SELECTION
)
from cocktail.controllers.userfilter import user_filters_registry
from cocktail.controllers.parameters import (
    get_parameter,
    FormSchemaReader,
    CookieParameterSource,
    set_cookie_expiration
)


class UserCollection(object):

    base_collection = None
    default_page_size = 15
    selection_mode = MULTIPLE_SELECTION
    available_languages = ()
    default_order = None

    allow_type_selection = True
    allow_member_selection = True
    allow_language_selection = True
    allow_filters = True
    allow_sorting = True
    allow_grouping = True
    allow_paging = True

    def __init__(self, root_type):
        self._root_type = root_type
        self.__base_filters = []
        self.__parameter_sources = {}
        self.__default_source = lambda k: self.get_parameter_source(k)(k)
    
    # Parameters
    #--------------------------------------------------------------------------
    @cached_getter
    def params(self):
        params = FormSchemaReader(strict = True)
        params.source = self.__default_source
        return params

    def get_parameter_source(self, param_name):
        source = self.params.source

        if source is self.__default_source:
            source = self.__parameter_sources.get(param_name)
            if source is None:
                source = cherrypy.request.params.get
        
        return source

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

        if type is None:
            return self._root_type

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
                    default_type = set,
                    items = schema.String(enumeration = self.public_members),
                    default = members
                )
            ) or members

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
        
        languages = set([get_language()])

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
        return user_filters_registry.get(self.type)

    def should_ignore_filter(self, filter):
        return False

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

            # If no filter is selected, select all promoted filters
            if not filters_param:
                filters_param = (
                    self.type.promoted_search_list
                    or [filter.id
                        for filter in self.available_user_filters
                        if filter.promoted_search]
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
                        set_cookie_expiration(response_cookie, seconds = 0) 
                        response_cookie["path"] = "/"

            if filters_param:
                
                available_filters = dict(
                    (filter.id, filter)
                    for filter in self.available_user_filters)

                for i, filter_id in enumerate(filters_param):
                    filter_model = available_filters.get(filter_id)
                    if filter_model:
                        filter = copy(filter_model)
                        filter.available_languages = self.available_languages
                        get_parameter(
                            filter.schema,
                            target = filter,
                            source = filter_source,
                            prefix = (self.params.prefix or "") + "filter_",
                            suffix = (self.params.suffix or "") + str(i)
                        )
                        if not self.should_ignore_filter(filter):
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
                        sign = NegativeExpression
                        key = key[1:]
                    else:
                        sign = PositiveExpression

                    member = self._get_member(
                        key,
                        translatable = True,
                        from_type = True
                    )

                    if member:
                        order.append(sign(member))

        if not order and self.default_order:
            order = self.default_order

        return ListWrapper(order)
    
    # Grouping
    #------------------------------------------------------------------------------
    @cached_getter
    def grouping(self):

        grouping = None

        if self.allow_grouping:
            
            grouping_param = self.params.read(schema.String("grouping"))

            if grouping_param:

                # Ascending / descending
                if grouping_param.startswith("-"):
                    sign = NegativeExpression
                    grouping_param = grouping_param[1:]
                else:
                    sign = PositiveExpression
                
                # Grouping variant
                pos = grouping_param.find("!")
                if pos != -1:
                    variant = grouping_param[pos+1:]
                    grouping_param = grouping_param[:pos]
                else:
                    variant = None

                # Groupped member
                member = self._get_member(
                    grouping_param,
                    translatable = True,
                    from_type = True
                )

                if isinstance(member, TranslationExpression):
                    member, language = (
                        member.operands[0],
                        member.operands[1].value
                    )
                else:
                    language = None
                
                if member and member.grouping:
                    grouping_class = resolve(member.grouping)
                    grouping = grouping_class()
                    grouping.member = member
                    grouping.sign = sign
                    grouping.language = language
                    grouping.variant = variant                    

        return grouping

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
                expression = user_filter.expression
                if expression is not None:
                    subset.add_filter(expression)

        if self.grouping:
            subset.add_order(self.grouping.order)
        
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

    # Exportation
    #------------------------------------------------------------------------------
    def export_file(self, dest, mime_type = None, **kwargs):
        """Exports the user_collection to a file"""
        members = [member
            for member in self.schema.ordered_members()
            if member.name in self.members]

        export_file(self.subset, dest, self.type, mime_type, members, **kwargs)
