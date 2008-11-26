#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
import cherrypy
from cocktail.modeling import ListWrapper, SetWrapper, getter, empty_set
from cocktail.persistence.query import Query
from cocktail.schema.expressions import (
    PositiveExpression,
    NegativeExpression
)
from cocktail.html.datadisplay import (
    NO_SELECTION, SINGLE_SELECTION, MULTIPLE_SELECTION
)
from cocktail.controllers.viewstate import get_persistent_param


class UserCollection(object):

    name = None

    base_collection = None

    allow_paging = True
    allow_sorting = True
    allow_filters = True
    allow_member_selection = True

    page = 0
    page_size = 15

    selection = None
    selection_mode = MULTIPLE_SELECTION
    selection_parser = int

    available_filters = ()

    persistence_prefix = None
    persistence_duration = -1
    persistent_params = empty_set

    def __init__(self,
        entity_type,
        schema = None,
        public_members = None):
        
        self.__entity_type = entity_type
        self.__schema = schema or entity_type
        
        if public_members is None:
            public_members = set(self.__schema.members().iterkeys())
        else:
            public_members = set(
                member if isinstance(member, basestring) else member.name
                for member in public_members
            )

        self.public_members = public_members
        self.__members_wrapper = None
        
        self.__base_filters = []
        self.base_filters = ListWrapper(self.__base_filters)

        self.__filters = []
        self.filters = ListWrapper(self.__filters)
        
        self.__user_filters = []
        self.user_filters = ListWrapper(self.__user_filters)

        self.__order = []
        self.order = ListWrapper(self.__order)
    
    @getter
    def entity_type(self):
        return self.__entity_type

    @getter
    def schema(self):
        return self.__schema

    @getter
    def members(self):
        if self.__members_wrapper is None:
            self.__members_wrapper = SetWrapper(
                set(
                    member.name
                    for member in self.__schema.members().itervalues()
                    if member.listed_by_default
                )
            )
        
        return self.__members_wrapper

    def add_base_filter(self, expression):
        self.__base_filters.append(expression)
    
    def subset(self):
        
        subset = Query(
            self.entity_type,
            base_collection = self.base_collection
        )
        
        for expression in self.__base_filters:
            subset.add_filter(expression)

        for expression in self.__filters:
            subset.add_filter(expression)

        for user_filter in self.__user_filters:
            subset.add_filter(user_filter.expression)

        for criteria in self.__order:
            subset.add_order(criteria)

        return subset
    
    def page_subset(self):
        
        subset = self.subset()

        if self.page_size is not None:
            start = self.page * self.page_size
            end = (self.page + 1) * self.page_size
            subset = subset[start:end]
        
        return subset

    def read(self):
        
        if self.allow_paging:
            self._read_paging()

        if self.allow_sorting:
            self._read_sorting()

        if self.allow_filters:
            self._read_filters()

        if self.allow_member_selection:
            self._read_member_selection()

        if self.selection_mode != NO_SELECTION:
            self._read_selection()

    def _get_param(self, name):

        full_name = self.get_param_name(name)
        
        if name in self.persistent_params:

            if self.persistence_prefix:
                cookie_name = self.persistence_prefix + "-" + full_name
            else:
                cookie_name = full_name
            
            return get_persistent_param(
                full_name,
                cookie_name = cookie_name,
                cookie_duration = self.persistence_duration                
            )
        else:
            return cherrypy.request.params.get(full_name)

    def _read_paging(self):

        page_param = self._get_param("page")
        
        if page_param:
            self.page = int(page_param)

        page_size_param = self._get_param("page_size")

        if page_size_param:
            self.page_size = int(page_size_param)

    def _read_sorting(self):

        order_param = self._get_param("order")

        if order_param:

            if isinstance(order_param, basestring):
                order_param = order_param.split(",")

            if self.__order:
                self.__order = []
                self.order = ListWrapper(order)

            for key in order_param:

                if key.startswith("-"):
                    sign = NegativeExpression
                    key = key[1:]
                else:
                    sign = PositiveExpression

                member = self._get_member(
                    key,
                    translatable = True,
                    from_entity = True
                )

                if member:
                    self.__order.append(sign(member))

    def _read_filters(self):
        
        filters_param = self._get_param("filters")
        
        if filters_param:
            if isinstance(filters_param, basestring):
                filters_param = [filters_param]

            for i, filter_type_id in enumerate(filters_param):                               
                for filter_type in self.available_filters:
                    if filter_type.filter_type_id == filter_type_id:
                        filter = filter_type()
                        get_parameter(
                            filter.schema,
                            target = filter,
                            suffix = str(i)
                        )
                        self.__user_filters.append(filter)
                else:
                    raise ValueError("Unknown filter: " + filter_type_id)

    def _read_member_selection(self):
        
        members_param = self._get_param("members")

        if members_param:

            if isinstance(members_param, basestring):
                members_param = members_param.split(",")

            members = set()
            self.__members_wrapper = SetWrapper(members)

            for key in members_param:
                if self._get_member(key):
                    members.add(key)

    def _read_selection(self):

        selection_param = self._get_param("selection")

        if selection_param:
            
            if self.selection_mode == SINGLE_SELECTION:
                self.selection = self.selection_parser(selection_param)
            else:
                if isinstance(selection_param, basestring):
                    selection_param = selection_param.split(",")

                self.selection = [
                    self.selection_parser(value)
                    for value in selection_param
                ]

    def get_param_name(self, param):
        if self.name:
            return self.name + "-" + param
        else:
            return param

    def _get_member(self, key, translatable = False, from_entity = False):
        
        if translatable:
            parts = key.split(".")
            name = parts[0]
        else:
            name = key

        try:
            schema = self.__entity_type if from_entity else self.__schema
            member = schema[name]
        except KeyError:
            member = None
    
        if member is None or name not in self.public_members:
            return None

        if translatable and len(parts) > 1:
            member = member.translated_into(parts[1])

        return member

