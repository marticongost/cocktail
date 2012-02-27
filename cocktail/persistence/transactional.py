#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from functools import wraps
from ZODB.POSException import ConflictError
from cocktail.styled import styled
from cocktail.persistence.datastore import datastore

verbose = True

def transactional(*trans_args, **trans_kwargs):
    
    def decorator(action):
    
        @wraps(action)
        def wrapper(*action_args, **action_kwargs):
            return transaction(
                lambda: action(*action_args, **action_kwargs), 
                *trans_args,
                **trans_kwargs
            )

        return wrapper
    
    return decorator

def transaction(action, max_attempts = 3, before_retrying = None, desist = None):

    for i in range(max_attempts):
        if i > 0:
            if verbose:
                print styled(
                    "Retrying transaction %s (%d/%d)" % (
                        action,
                        i,
                        max_attempts - 1
                    ), 
                    {1: "yellow", 2: "brown", 3: "red"}.get(i, "violet")
                )
            if before_retrying is not None:
                before_retrying()
        try:
            rvalue = action(*args, **kwargs)
            datastore.commit()
            return rvalue
        except ConflictError:
            datastore.abort()
            datastore.sync()
            if desist is not None and desist():
                break
    raise

