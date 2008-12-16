#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.modeling import ListWrapper, empty_list


class ErrorList(ListWrapper):

    def __init__(self, errors):
    
        ListWrapper.__init__(self)
        self.__errors_by_member = {}

        for error in errors:
            self.add(error)

    def _normalize_member(self, member):
        if not isinstance(member, basestring):
            member = member.name

        return member

    def add(self, error):
        
        self._items.append(error)

        if error.member:
            key = (self._normalize_member(error.member), error.language)
            member_errors = self.__errors_by_member.get(key)
            
            if member_errors is None:
                self.__errors_by_member[key] = [error]
            else:
                member_errors.append(error)

    def in_member(self, member, language = None):
        return self.__errors_by_member.get(
            (self._normalize_member(member), language),
            empty_list
        )

