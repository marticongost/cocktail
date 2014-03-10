#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from functools import wraps
from ZODB.POSException import ConflictError
from cocktail.styled import styled
from cocktail.persistence.datastore import datastore

verbose = True
desisted = object()

def transactional(*transaction_args, **transaction_kwargs):
    
    def decorator(action):
    
        @wraps(action)
        def wrapper(*action_args, **action_kwargs):
            return transaction(
                action,
                action_args,
                action_kwargs,
                *transaction_args,
                **transaction_kwargs
            )

        return wrapper
    
    return decorator

def transaction(
    action, 
    action_args = (),
    action_kwargs = None,
    max_attempts = 3,
    before_retrying = None,
    desist = None
):
    if action_kwargs is None:
        action_kwargs = {}

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
                before_retrying(*action_args, **action_kwargs)

            if desist is not None and desist(*action_args, **action_kwargs):
                return desisted
        try:
            rvalue = action(*action_args, **action_kwargs)
            datastore.commit()
            return rvalue
        except ConflictError:
            datastore.sync() # implicit abort
    
    raise

