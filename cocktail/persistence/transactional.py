#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from functools import wraps
from ZODB.POSException import ConflictError
from cocktail.styled import styled
from cocktail.persistence.datastore import datastore

verbose = True

def transactional(max_attempts = 3, before_retrying = None):
    
    def decorator(transactional_code):
    
        @wraps(transactional_code)
        def wrapper(*args, **kwargs):

            for i in range(max_attempts):
                if i > 0:
                    if verbose:
                        print styled(
                            "Retrying transaction %s (%d/%d)" % (
                                transactional_code,
                                i,
                                max_attempts - 1
                            ), 
                            {1: "yellow", 2: "brown", 3: "red"}.get(i, "violet")
                        )
                    if before_retrying is not None:
                        before_retrying()
                try:
                    rvalue = transactional_code(*args, **kwargs)
                    datastore.commit()
                    return rvalue
                except ConflictError:
                    datastore.abort()
                    datastore.sync()
            
            raise

        return wrapper
    
    return decorator

